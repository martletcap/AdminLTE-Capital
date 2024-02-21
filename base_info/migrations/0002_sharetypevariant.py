# Generated by Django 4.1.12 on 2024-02-21 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_info', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareTypeVariant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('variant', models.CharField(max_length=255, unique=True)),
                ('share_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_info.sharetype')),
            ],
            options={
                'db_table': 'share_type_variant',
            },
        ),
    ]
