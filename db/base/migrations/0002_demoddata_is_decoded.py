# Generated by Django 1.11.10 on 2018-03-04 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_squashed_0009_auto_20180103_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoddata',
            name='is_decoded',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
