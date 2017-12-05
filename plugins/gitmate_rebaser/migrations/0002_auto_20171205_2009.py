# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-05 20:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_rebaser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='repo',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gitmate_rebaser_settings', to='gitmate_config.Repository'),
        ),
    ]
