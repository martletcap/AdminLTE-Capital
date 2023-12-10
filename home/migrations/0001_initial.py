# Generated by Django 4.1.12 on 2023-12-10 15:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryOfCompany',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'category_of_company',
                'ordering': ['category'],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('short_name', models.CharField(max_length=256)),
                ('comment', models.TextField(max_length=1024)),
                ('link', models.URLField()),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.categoryofcompany')),
            ],
            options={
                'db_table': 'company',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CompanyStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'company_status',
                'ordering': ['status'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=128)),
                ('comment', models.TextField(max_length=1024)),
                ('website', models.URLField()),
            ],
            options={
                'db_table': 'contact',
            },
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'contact_type',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=128)),
                ('country', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'sector',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('comment', models.TextField(max_length=1024)),
                ('add_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.company')),
            ],
            options={
                'db_table': 'share',
            },
        ),
        migrations.CreateModel(
            name='ShareType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'share_type',
                'ordering': ['type'],
            },
        ),
        migrations.CreateModel(
            name='SharePrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=4, max_digits=12)),
                ('date', models.DateField()),
                ('share', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.share')),
            ],
            options={
                'db_table': 'share_price',
            },
        ),
        migrations.CreateModel(
            name='Shareholder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('complite', models.BooleanField()),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_edit_datetime', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(max_length=1024)),
                ('add_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shareholder_add', to=settings.AUTH_USER_MODEL)),
                ('last_edit_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shareholder_edit', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.contact')),
                ('share', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.share')),
            ],
            options={
                'db_table': 'shareholder',
            },
        ),
        migrations.AddField(
            model_name='share',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.sharetype'),
        ),
        migrations.CreateModel(
            name='SeedStep',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_term', models.DateField()),
                ('end_term', models.DateField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.company')),
            ],
            options={
                'db_table': 'seed_step',
                'ordering': ['-end_term'],
            },
        ),
        migrations.CreateModel(
            name='OurTransaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('amount', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=4, max_digits=12)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_edit_datetime', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(max_length=1024)),
                ('add_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='our_transaction_add', to=settings.AUTH_USER_MODEL)),
                ('last_edit_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='our_transaction_edit', to=settings.AUTH_USER_MODEL)),
                ('share', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.share')),
            ],
            options={
                'db_table': 'our_transaction',
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='contact',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.contacttype'),
        ),
        migrations.AddField(
            model_name='company',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.contact'),
        ),
        migrations.AddField(
            model_name='company',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.location'),
        ),
        migrations.AddField(
            model_name='company',
            name='sector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.sector'),
        ),
        migrations.AddField(
            model_name='company',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='home.companystatus'),
        ),
    ]
