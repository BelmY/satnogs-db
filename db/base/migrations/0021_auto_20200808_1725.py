# Generated by Django 2.2.15 on 2020-08-08 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_auto_20200802_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demoddata',
            name='timestamp',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]