# Generated by Django 2.0.1 on 2018-01-23 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_artist'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='genre',
            field=models.CharField(default='null', max_length=100),
            preserve_default=False,
        ),
    ]
