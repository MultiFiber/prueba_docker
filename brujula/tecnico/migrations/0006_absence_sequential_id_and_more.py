# Generated by Django 4.0.5 on 2022-12-12 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0005_rangeofhoursavailable_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='absence',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalabsence',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalholiday',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaltechnician',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='holiday',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='technician',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
