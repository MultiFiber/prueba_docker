# Generated by Django 4.0.5 on 2023-01-19 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0010_remove_disponibility_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='absence',
            name='schedule_day',
        ),
        migrations.RemoveField(
            model_name='historicalabsence',
            name='schedule_day',
        ),
    ]