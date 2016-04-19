# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-18 01:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrestia', '0018_auto_20160418_0032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='delegatesummary',
            options={'ordering': ('state__name',), 'verbose_name_plural': 'delegate_summaries'},
        ),
        migrations.AddField(
            model_name='delegatesummary',
            name='available_pledged',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='delegatesummary',
            name='available_unpledged',
            field=models.IntegerField(default=0),
        ),
    ]