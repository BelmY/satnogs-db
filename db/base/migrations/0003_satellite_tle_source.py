# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-09-19 00:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_demoddata_is_decoded'),
    ]

    operations = [
        migrations.AddField(
            model_name='satellite',
            name='tle_source',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]