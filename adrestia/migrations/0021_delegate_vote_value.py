# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-21 08:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrestia', '0020_auto_20160420_0712'),
    ]

    operations = [
        migrations.AddField(
            model_name='delegate',
            name='vote_value',
            field=models.DecimalField(decimal_places=1, default=1.0, max_digits=2),
        ),
    ]
