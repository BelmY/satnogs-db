# Generated by Django 3.1.5 on 2021-01-20 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_set_tle_ondelete_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoddata',
            name='version',
            field=models.CharField(blank=True, max_length=45),
        ),
    ]
