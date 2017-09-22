# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-24 20:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gitmate_config', '0009_auto_20170622_1147'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=255)),
                ('provider', models.CharField(default=None, max_length=32)),
                ('masters', models.ManyToManyField(related_name='orgs', to=settings.AUTH_USER_MODEL)),
                ('primary_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='organization',
            unique_together=set([('provider', 'name')]),
        ),
    ]
