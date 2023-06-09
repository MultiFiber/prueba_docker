# Generated by Django 4.0.5 on 2022-12-19 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('OS', '0005_alter_displacement_km_final_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicaltripsummary',
            old_name='km_init',
            new_name='km_initial',
        ),
        migrations.RenameField(
            model_name='tripsummary',
            old_name='km_init',
            new_name='km_initial',
        ),
        migrations.AddField(
            model_name='displacement',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaldisplacement',
            name='sequential_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalospic',
            name='caption',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='historicalospic',
            name='photo',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='historicaltripsummary',
            name='time',
            field=models.TimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ospic',
            name='caption',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='ospic',
            name='owner_os',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_os', to='OS.os'),
        ),
        migrations.AlterField(
            model_name='ospic',
            name='photo',
            field=models.ImageField(upload_to='photos'),
        ),
        migrations.AlterField(
            model_name='tripsummary',
            name='time',
            field=models.TimeField(auto_now_add=True, null=True),
        ),
    ]
