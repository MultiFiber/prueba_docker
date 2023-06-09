# Generated by Django 3.2.16 on 2022-11-26 22:37

from django.db import migrations, models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Displacement',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('km_init', models.IntegerField()),
                ('km_final', models.IntegerField()),
                ('medio_desplazamiento', models.IntegerField(choices=[(0, 'Vehiculo Particular'), (1, 'Motocicleta'), (2, 'Bus'), (3, 'Tren')], default=0)),
                ('displacement_time', models.TimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Displacement',
                'verbose_name_plural': 'Displacements',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDisplacement',
            fields=[
                ('ID', models.IntegerField(blank=True, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, editable=False)),
                ('date', models.DateTimeField(blank=True, editable=False, null=True)),
                ('km_init', models.IntegerField()),
                ('km_final', models.IntegerField()),
                ('medio_desplazamiento', models.IntegerField(choices=[(0, 'Vehiculo Particular'), (1, 'Motocicleta'), (2, 'Bus'), (3, 'Tren')], default=0)),
                ('displacement_time', models.TimeField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical Displacement',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOs',
            fields=[
                ('ID', models.IntegerField(blank=True, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, editable=False)),
                ('status', models.IntegerField(choices=[(0, 'Agendada'), (1, 'En desplazamiento'), (2, 'En atendimiento'), (3, 'Pausada'), (4, 'En espera del cliente'), (5, 'Cancelada'), (6, 'No se pudo instalar'), (7, 'Por reagendar'), (8, 'Finalizada')], default=0)),
                ('technology', models.CharField(max_length=20)),
                ('plan', models.IntegerField(blank=True, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('sequential_id', models.IntegerField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical Os',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOsPic',
            fields=[
                ('ID', models.IntegerField(blank=True, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, editable=False)),
                ('photo', models.TextField(max_length=100, verbose_name='photo')),
                ('caption', models.CharField(max_length=255, verbose_name='caption')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical OSPic',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Os',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(choices=[(0, 'Agendada'), (1, 'En desplazamiento'), (2, 'En atendimiento'), (3, 'Pausada'), (4, 'En espera del cliente'), (5, 'Cancelada'), (6, 'No se pudo instalar'), (7, 'Por reagendar'), (8, 'Finalizada')], default=0)),
                ('technology', models.CharField(max_length=20)),
                ('plan', models.IntegerField(blank=True, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('sequential_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Os',
                'verbose_name_plural': "OS's",
            },
        ),
        migrations.CreateModel(
            name='OsPic',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('photo', models.ImageField(upload_to='photos', verbose_name='photo')),
                ('caption', models.CharField(max_length=255, verbose_name='caption')),
            ],
            options={
                'verbose_name': 'OSPic',
                'verbose_name_plural': 'OSPics',
            },
        ),
    ]
