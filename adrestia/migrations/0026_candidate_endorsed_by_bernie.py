# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-28 00:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrestia', '0025_auto_20160515_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='endorsed_by_bernie',
            field=models.BooleanField(default=False, help_text='Endorsed by Bernie'),
            preserve_default=False,
        ),
    ]
