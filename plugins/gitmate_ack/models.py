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
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE,
                             related_name='ack_mrs')
    number = models.IntegerField()
    acks = psql_fields.JSONField(default={})
    last_head = models.CharField(default='', max_length=40)

    @property
    def ack_state(self):
        state = CommitStatus(
            Status.SUCCESS, 'This PR is reviewed. :)',
            'review/gitmate/manual/pr', 'https://gitmate.io')
        for acked in dict(self.acks).values():
            if acked['status'] in [Status.FAILED.value,
                                   Status.ERROR.value,
                                   Status.CANCELED.value]:
                return CommitStatus(
                    Status.FAILED, 'This PR needs work. :(',
                    'review/gitmate/manual/pr', 'https://gitmate.io')
            if acked['status'] == Status.PENDING.value:
                state = CommitStatus(
                    Status.PENDING, 'This PR needs review.',
                    'review/gitmate/manual/pr', 'https://gitmate.io')

        return state
