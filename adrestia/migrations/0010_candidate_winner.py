# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-11 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrestia', '0009_auto_20160411_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='winner',
            field=models.BooleanField(default=False),
        ),
    ]
