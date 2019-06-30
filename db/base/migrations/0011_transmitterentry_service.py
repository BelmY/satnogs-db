# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-02 05:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20190421_0143'),
    ]

    operations = [
        migrations.AddField(
            model_name='transmitterentry',
            name='service',
            field=models.CharField(choices=[('Aeronautical', 'Aeronautical'), ('Amateur', 'Amateur'), ('Broadcasting', 'Broadcasting'), ('Earth Exploration', 'Earth Exploration'), ('Fixed', 'Fixed'), ('Inter-satellite', 'Inter-satellite'), ('Maritime', 'Maritime'), ('Meteorological', 'Meteorological'), ('Mobile', 'Mobile'), ('Radiolocation', 'Radiolocation'), ('Radionavigational', 'Radionavigational'), ('Space Operation', 'Space Operation'), ('Space Research', 'Space Research'), ('Standard Frequency and Time Signal', 'Standard Frequency and Time Signal'), ('Unknown', 'Unknown')], default='Unknown', max_length=34),
        ),
    ]
