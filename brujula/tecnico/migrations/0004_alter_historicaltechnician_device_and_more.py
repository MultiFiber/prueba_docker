# Generated by Django 4.0.5 on 2022-12-02 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0003_alter_absence_creator_alter_absence_updater_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltechnician',
            name='device',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='technician',
            name='device',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]