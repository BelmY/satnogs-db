# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-07 12:40
from __future__ import unicode_literals

import db.base.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import shortuuidfield.fields


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# db.base.migrations.0009_auto_20180103_1931

class Migration(migrations.Migration):

    replaces = [('base', '0001_initial'), ('base', '0002_auto_20150908_2054'), ('base', '0003_auto_20160504_2104'), ('base', '0004_auto_20170302_1641'), ('base', '0005_demoddata_observer'), ('base', '0006_auto_20170323_1715'), ('base', '0007_satellite_status'), ('base', '0008_satellite_description'), ('base', '0009_auto_20180103_1931')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Satellite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('norad_cat_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=45)),
                ('names', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, help_text='Ideally: 250x250', upload_to='satellites')),
                ('tle1', models.CharField(blank=True, max_length=200)),
                ('tle2', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('alive', 'alive'), ('dead', 'dead'), ('re-entered', 're-entered')], default='alive', max_length=10)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['norad_cat_id'],
            },
        ),
        migrations.CreateModel(
            name='Transmitter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', shortuuidfield.fields.ShortUUIDField(blank=True, db_index=True, editable=False, max_length=22, unique=True)),
                ('description', models.TextField()),
                ('alive', models.BooleanField(default=True)),
                ('uplink_low', models.PositiveIntegerField(blank=True, null=True)),
                ('uplink_high', models.PositiveIntegerField(blank=True, null=True)),
                ('downlink_low', models.PositiveIntegerField(blank=True, null=True)),
                ('downlink_high', models.PositiveIntegerField(blank=True, null=True)),
                ('invert', models.BooleanField(default=False)),
                ('baud', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('transmitter_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.Transmitter')),
                ('citation', models.CharField(blank=True, max_length=255)),
            ],
            bases=('base.transmitter',),
        ),
        migrations.AddField(
            model_name='transmitter',
            name='mode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transmitters', to='base.Mode'),
        ),
        migrations.AddField(
            model_name='transmitter',
            name='satellite',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transmitters', to='base.Satellite'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='transmitter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suggestions', to='base.Transmitter'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='DemodData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_id', models.PositiveIntegerField(blank=True, null=True)),
                ('transmitter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Transmitter')),
                ('lat', models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(90), django.core.validators.MinValueValidator(-90)])),
                ('lng', models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(180), django.core.validators.MinValueValidator(-180)])),
                ('payload_decoded', models.TextField(blank=True)),
                ('payload_frame', models.FileField(blank=True, null=True, upload_to=db.base.models._name_payload_frame)),
                ('satellite', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telemetry_data', to='base.Satellite')),
                ('source', models.CharField(choices=[('manual', 'manual'), ('network', 'network'), ('sids', 'sids')], default='sids', max_length=7)),
                ('station', models.CharField(default='Unknown', max_length=45)),
                ('timestamp', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Telemetry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('schema', models.TextField(blank=True)),
                ('decoder', models.CharField(blank=True, max_length=20)),
                ('satellite', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telemetries', to='base.Satellite')),
            ],
            options={
                'ordering': ['satellite__norad_cat_id'],
                'verbose_name_plural': 'Telemetries',
            },
        ),
        migrations.AddField(
            model_name='demoddata',
            name='payload_telemetry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Telemetry'),
        ),
        migrations.AddField(
            model_name='demoddata',
            name='observer',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]
