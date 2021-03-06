# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-15 11:19
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gitmate_config', '0009_auto_20170622_1147'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keywords', django.contrib.postgres.fields.jsonb.JSONField(default={}, help_text='Comma seperated keywords (values) triggering assignees (keys) to be set; e.g. sils: bug, crash.')),
                ('repo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gitmate_issue_assigner_repository', to='gitmate_config.Repository')),
            ],
            options={
                'verbose_name_plural': 'settings',
                'abstract': False,
            },
        ),
    ]
