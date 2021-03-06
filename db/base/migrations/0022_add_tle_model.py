# Generated by Django 2.2.14 on 2020-08-03 02:04

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_auto_20200808_1725'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tle0', models.CharField(blank=True, max_length=69, validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(69)])),
                ('tle1', models.CharField(blank=True, max_length=69, validators=[django.core.validators.MinLengthValidator(69), django.core.validators.MaxLengthValidator(69)])),
                ('tle2', models.CharField(blank=True, max_length=69, validators=[django.core.validators.MinLengthValidator(69), django.core.validators.MaxLengthValidator(69)])),
                ('tle_source', models.CharField(blank=True, max_length=300)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('satellite', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tles', to='base.Satellite')),
            ],
            options={
                'ordering': ['-updated'],
            },
        ),
        migrations.CreateModel(
            name='LatestTle',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('base.tle',),
        ),
        migrations.AddIndex(
            model_name='tle',
            index=models.Index(fields=['-updated'], name='base_tle_updated_8936f7_idx'),
        ),
        migrations.AddIndex(
            model_name='tle',
            index=models.Index(fields=['tle1', 'tle2', 'tle_source', 'satellite'], name='base_tle_tle1_30ea48_idx'),
        ),
        migrations.AddConstraint(
            model_name='tle',
            constraint=models.UniqueConstraint(fields=('tle1', 'tle2', 'tle_source', 'satellite'), name='unique_entry_from_source_for_satellite'),
        ),
    ]
