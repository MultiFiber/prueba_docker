# Generated by Django 4.0.5 on 2022-12-12 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0005_merge_20221206_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcategory',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]