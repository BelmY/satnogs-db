# Generated by Django 2.2.11 on 2020-05-20 14:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import db.base.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0016_increase_mode_name_char_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportedFrameset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('exported_file', models.FileField(blank=True, null=True, upload_to=db.base.models._name_exported_frames)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('satellite', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Satellite')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
