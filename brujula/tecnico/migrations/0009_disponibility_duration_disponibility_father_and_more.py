# Generated by Django 4.0.5 on 2023-01-12 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0008_absence_type_historicalabsence_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='disponibility',
            name='duration',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='disponibility',
            name='father',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tecnico.disponibility'),
        ),
        migrations.AddField(
            model_name='historicaldisponibility',
            name='duration',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='historicaldisponibility',
            name='father',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tecnico.disponibility'),
        ),
        migrations.AlterField(
            model_name='historicalschedule',
            name='schedule_end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='historicalschedule',
            name='schedule_start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='schedule_end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='schedule_start_date',
            field=models.DateField(),
        ),
    ]
