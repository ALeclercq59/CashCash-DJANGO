# Generated by Django 3.0.6 on 2020-05-28 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sitePPE', '0002_auto_20200528_2326'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='intervention',
            options={'ordering': ['date_visite']},
        ),
    ]