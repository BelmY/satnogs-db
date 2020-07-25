# Generated by Django 2.2.14 on 2020-07-15 12:02

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_artifact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('names', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='satellite',
            name='countries',
            field=django_countries.fields.CountryField(blank=True, max_length=746, multiple=True),
        ),
        migrations.AddField(
            model_name='satellite',
            name='deployed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='satellite',
            name='launched',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='satellite',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='satellite',
            name='operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='satellite_operator', to='base.Operator'),
        ),
    ]