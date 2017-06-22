from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest


from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.scheduler(
    5.0
)
def add():
	from gitmate_config.models import Repository
	repo_obj = Repository.objects.filter(
		active=True,
		provider='github').first()
	for x in range(10):
		ResponderRegistrar.respond(MergeRequestActions.COMMENTED,
			repo_obj,
    		2,2,x)

@ResponderRegistrar.responder(
	'stale_pr_pinger',
	MergeRequestActions.COMMENTED)
def git_stale_pr_pinger(a,b,num):
	print("stale_task %d: %d"%(num,a+b))