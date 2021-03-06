# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-13 14:22
from __future__ import unicode_literals

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
                ('repo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gitmate_rebaser_repository', to='gitmate_config.Repository')),
            ],
            options={
                'verbose_name_plural': 'settings',
                'abstract': False,
            },
        ),
    ]
