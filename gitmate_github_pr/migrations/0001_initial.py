# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 14:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gitmate_config', '0004_auto_20170214_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autorespond_active', models.BooleanField(default=False)),
                ('autorespond_text', models.TextField(max_length=2500)),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='github_pr_repository', to='gitmate_config.Repository')),
            ],
        ),
    ]