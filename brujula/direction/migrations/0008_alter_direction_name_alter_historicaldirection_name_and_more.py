# Generated by Django 4.0.5 on 2023-04-03 17:39

import django.contrib.postgres.indexes
from django.db import migrations, models
from django.contrib.postgres.operations import BtreeGinExtension
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('direction', '0007_alter_direction_name_alter_historicaldirection_name'),
    ]

    operations = [
        UnaccentExtension(),
        BtreeGinExtension(), 
        migrations.AlterField(
            model_name='direction',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='historicaldirection',
            name='name',
            field=models.TextField(),
        ),
        migrations.AddIndex(
            model_name='direction',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name', 'full_direction'], name='busqueda_direccion_1'),
        ),
        
    ]
