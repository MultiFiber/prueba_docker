# Generated by Django 4.1.5 on 2023-03-29 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0006_category_sequential_id_and_more'),
        ('tecnico', '0015_alter_absence_status_alter_historicalabsence_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='technician',
            name='categories',
            field=models.ManyToManyField(to='category.category'),
        ),
    ]