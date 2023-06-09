# Generated by Django 4.0.5 on 2023-02-22 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0014_alter_absence_time_end_alter_absence_time_start_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pendiente'), (1, 'Aprobada'), (2, 'Rechazada')]),
        ),
        migrations.AlterField(
            model_name='historicalabsence',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pendiente'), (1, 'Aprobada'), (2, 'Rechazada')]),
        ),
        migrations.AlterField(
            model_name='historicaltechnician',
            name='id_type',
            field=models.IntegerField(choices=[(0, 'pasaporte'), (1, 'dni'), (2, 'rut'), (3, 'cedula'), (4, 'pasaporte'), (5, 'dni'), (6, 'ce')]),
        ),
        migrations.AlterField(
            model_name='technician',
            name='id_type',
            field=models.IntegerField(choices=[(0, 'pasaporte'), (1, 'dni'), (2, 'rut'), (3, 'cedula'), (4, 'pasaporte'), (5, 'dni'), (6, 'ce')]),
        ),
    ]
