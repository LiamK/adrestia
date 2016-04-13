# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-12 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrestia', '0012_auto_20160412_2056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='facebook_url',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='twitter_url',
        ),
        migrations.AddField(
            model_name='candidate',
            name='facebook_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='twitter_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]