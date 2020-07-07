from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satellite',
            name='image',
            field=models.ImageField(help_text='Ideally: 250x250', upload_to='satellites', blank=True),
        ),
    ]
