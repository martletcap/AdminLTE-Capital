# Generated by Django 4.1.12 on 2023-12-05 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='company',
            table='company',
        ),
        migrations.AlterModelTable(
            name='location',
            table='location',
        ),
        migrations.AlterModelTable(
            name='sector',
            table='sector',
        ),
        migrations.AlterModelTable(
            name='share',
            table='share',
        ),
    ]
