# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-22 11:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_code_analysis', '0003_auto_20170608_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysisresults',
            options={'verbose_name': 'result', 'verbose_name_plural': 'results'},
        ),
    ]