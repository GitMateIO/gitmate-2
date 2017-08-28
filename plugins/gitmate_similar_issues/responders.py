from celery.schedules import crontab
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.Repository import Repository
from sklearn.feature_extraction.text import TfidfVectorizer
from gitmate_hooks import ResponderRegistrar


def tfidf_similarity(X, Y=None):
    if Y is None:
        Y = X.T
    matrix = (X * Y).A
    return matrix


def find_similar_issues(issues: dict, similarity_threshold: float=0.5) -> dict:
    vect = TfidfVectorizer(min_df=0, ngram_range=(1, 5))
    tfidf = vect.fit_transform(list(issues.values()))
    matrix = tfidf_similarity(tfidf)

    return {
        id: {
            iss: score
            for iss, score in zip(issues.keys(), scores)
            if score > similarity_threshold and iss != id
        }
        for id, scores in zip(issues.keys(), matrix)
    }


def _update_issues(repo: Repository):
    # TODO: save issues of repository in database.
    pass


@ResponderRegistrar.scheduled_responder(
    'similar_issues', crontab(minute='0', hour='6,18'), is_active=True)
def update_issues(repo: Repository, **kwargs):
    _update_issues(repo)


@ResponderRegistrar.responder('similar_issues', IssueActions.OPENED, IssueActions.REOPENED)
def gitmate_similar_issues(issue: Issue, **kwargs):
    print('Lets go to work!')
    all_issues = list(issue.repository.filter_issues(state='all'))
    print(f'Im still here, {issue._token._token}')
    issue_dict = {issue.number: f'{issue.title} {issue.description}'
                  for issue in all_issues}
    print('Got all issues')

    sim_issues = find_similar_issues(issue_dict, similarity_threshold=0)
    issue.add_comment(f'Hey there! I got {str(sim_issues)}')
