# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-12 02:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrestia', '0026_candidate_endorsed_by_bernie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='district',
            field=models.CharField(blank=True, help_text='Fed or State house district name or number, Junior Seat or Senior Seat for Fed Senate, City for Mayor', max_length=64, null=True),
        ),
    ]
