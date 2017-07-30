from django.db import models
from django.contrib.postgres import fields as psql_fields

from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Issue import Issue

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    pass


class MergeRequestModel(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    number = models.IntegerField()
    closes_issues = psql_fields.JSONField(default={})

    @classmethod
    def find_mrs_with_issue(cls, issue: Issue):
        repo = Repository.from_igitt_repo(issue.repository)
        return cls.objects.filter(
            repo=repo, closes_issues__has_key=str(issue.number))

    @property
    def igitt_pr(self):
        return self.repo.igitt_repo.get_mr(self.number)
