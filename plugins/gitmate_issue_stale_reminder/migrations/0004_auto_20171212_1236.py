# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-12 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_issue_stale_reminder', '0003_auto_20171205_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='unassign',
            field=models.BooleanField(default=True, help_text='Unassign assignees if an issue goes stale'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='issue_expire_limit',
            field=models.IntegerField(default=30, help_text='No. of days after which an issue is considered stale'),
        ),
    ]
