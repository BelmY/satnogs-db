# Generated by Django 1.11.11 on 2019-01-19 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20181215_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='satellite',
            name='decayed',
            field=models.DateTimeField(null=True),
        ),
    ]
