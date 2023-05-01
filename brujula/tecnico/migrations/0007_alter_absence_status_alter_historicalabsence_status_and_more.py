# Generated by Django 4.0.5 on 2022-12-19 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0006_absence_sequential_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pendiente'), (1, 'Aprovada'), (2, 'Rechazada')]),
        ),
        migrations.AlterField(
            model_name='historicalabsence',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pendiente'), (1, 'Aprovada'), (2, 'Rechazada')]),
        ),
        migrations.AlterField(
            model_name='historicalholiday',
            name='status',
            field=models.IntegerField(choices=[(0, 'Activo'), (1, 'Inactivo')]),
        ),
        migrations.AlterField(
            model_name='historicaltechnicianpic',
            name='caption',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='historicaltechnicianpic',
            name='photo',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='holiday',
            name='status',
            field=models.IntegerField(choices=[(0, 'Activo'), (1, 'Inactivo')]),
        ),
        migrations.AlterField(
            model_name='technicianpic',
            name='caption',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='technicianpic',
            name='owner_tech',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_tech', to='tecnico.technician'),
        ),
        migrations.AlterField(
            model_name='technicianpic',
            name='photo',
            field=models.ImageField(upload_to='photos'),
        ),
    ]