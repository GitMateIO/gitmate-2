# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-03 10:54
from __future__ import unicode_literals

import django.contrib.postgres.fields
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
                ('status_labels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=40), help_text='Comma seperated labels to be removed from the merge request once it has been approved. e.g. process/WIP, status/stale, process/pending_review', size=None)),
                ('approved_label', models.CharField(default='status/approved', max_length=40)),
                ('repo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gitmate_test_approver_repository', to='gitmate_config.Repository')),
            ],
            options={
                'verbose_name_plural': 'settings',
                'abstract': False,
            },
        ),
    ]
