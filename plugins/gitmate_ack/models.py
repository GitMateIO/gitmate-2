from IGitt.Interfaces.Repository import Repository as IGittRepository
from IGitt.Interfaces.CommitStatus import Status, CommitStatus
from django.db import models
from django.contrib.postgres import fields as psql_fields

from gitmate_config.models import SettingsBase, Repository


class Settings(SettingsBase):
    ack_strs = models.CharField(
        default='ack, reack',
        max_length=100,
        help_text='Keywords for acknowledging commits, comma separated')
    unack_strs = models.CharField(
        default='unack',
        max_length=100,
        help_text='Keywords for unacknowledging commits, comma separated')


class MergeRequestModel(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    number = models.IntegerField()
    acks = psql_fields.JSONField(default={})

    @property
    def igitt_pr(self):
        return self.repo.igitt_repo.get_mr(self.number)

    @classmethod
    def find_mrs_with_commit(cls, repository: IGittRepository, sha: str):
        repo = Repository.from_igitt_repo(repository)
        return cls.objects.filter(
            repo=repo, acks__has_key=sha)

    @property
    def ack_state(self):
        state = CommitStatus(
            Status.SUCCESS, 'This PR is reviewed :)',
            'review/gitmate/manual/pr', 'https://gitmate.io')
        for commit, acked in self.acks.values():
            if acked is False:
                return CommitStatus(
                    Status.FAILED, 'This PR needs work',
                    'review/gitmate/manual/pr', 'https://gitmate.io')
            if acked is None:
                state = CommitStatus(
                    Status.PENDING, 'This PR needs review',
                    'review/gitmate/manual/pr', 'https://gitmate.io')

        return state
