# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-28 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_rebaser', '0005_auto_20180128_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='fastforward_admin_only',
            field=models.BooleanField(default=False, help_text='Only admins can fastforward if set to True, else anyone with write access can'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='merge_admin_only',
            field=models.BooleanField(default=False, help_text='Only admins can merge if set to True, else anyone with write access can'),
        ),
    ]
