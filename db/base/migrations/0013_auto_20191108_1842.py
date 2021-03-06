# Generated by Django 2.2.6 on 2019-11-08 18:42

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import F


def copy_field(apps, schema_editor):
    models = apps.get_model('base', 'TransmitterEntry')
    modes = apps.get_model('base', 'Mode')
    for transmitter in models.objects.all().iterator():
        if transmitter.type != "Transmitter":
            transmitter.uplink_mode = transmitter.downlink_mode
            if transmitter.invert == True:
                if transmitter.downlink_mode.name == "USB":
                    transmitter.uplink_mode = modes.objects.get(name="LSB")
                elif transmitter.downlink_mode.name == "LSB":
                    transmitter.uplink_mode = modes.objects.get(name="USB")

            transmitter.save()

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20191108_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='transmitterentry',
            name='uplink_mode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transmitter_uplink_entries', to='base.Mode'),
        ),
        migrations.AlterField(
            model_name='transmitterentry',
            name='downlink_mode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transmitter_downlink_entries', to='base.Mode'),
        ),
        migrations.RunPython(copy_field, reverse_code=migrations.RunPython.noop),
    ]
