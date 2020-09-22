# Generated by Django 2.2.14 on 2020-09-21 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0026_add_satellite_norad_follow_id_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satellite',
            name='status',
            field=models.CharField(choices=[('alive', 'alive'), ('dead', 'dead'), ('future', 'future'), ('re-entered', 're-entered')], default='alive', max_length=10),
        ),
    ]