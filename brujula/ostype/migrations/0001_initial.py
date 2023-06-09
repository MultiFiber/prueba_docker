# Generated by Django 3.2.16 on 2022-11-26 22:37

from django.db import migrations, models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalOstype',
            fields=[
                ('ID', models.IntegerField(blank=True, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('tag', models.CharField(max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical OStype',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Ostype',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('tag', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'OStype',
                'verbose_name_plural': 'OStypes',
            },
        ),
    ]
