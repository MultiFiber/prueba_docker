# Generated by Django 4.0.5 on 2022-12-12 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0002_historicaluserapp_operator_userapp_operator_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluserapp',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userapp',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
