# Generated by Django 4.0.5 on 2022-12-06 18:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tecnico', '0004_alter_historicaltechnician_device_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RangeOfHoursAvailable',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('time_init', models.TimeField()),
                ('time_final', models.TimeField()),
                ('status', models.IntegerField(choices=[(0, 'Disponible'), (1, 'No disponible'), (2, 'En almuerzo'), (3, 'Ausente')])),
                ('duration', models.IntegerField()),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creator', to=settings.AUTH_USER_MODEL)),
                ('disponibility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tecnico.disponibility')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updater', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Range Of Hours Available',
                'verbose_name_plural': 'Range Of Hours Availables',
            },
        ),
        migrations.CreateModel(
            name='HistoricalRangeOfHoursAvailable',
            fields=[
                ('ID', models.IntegerField(blank=True, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, editable=False)),
                ('time_init', models.TimeField()),
                ('time_final', models.TimeField()),
                ('status', models.IntegerField(choices=[(0, 'Disponible'), (1, 'No disponible'), (2, 'En almuerzo'), (3, 'Ausente')])),
                ('duration', models.IntegerField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('creator', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('disponibility', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tecnico.disponibility')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updater', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Range Of Hours Available',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
