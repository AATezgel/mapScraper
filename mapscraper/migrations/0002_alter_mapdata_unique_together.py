# Generated by Django 5.2.4 on 2025-07-19 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapscraper', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mapdata',
            unique_together={('name', 'address')},
        ),
    ]
