# Generated by Django 3.2.16 on 2022-11-26 22:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ostype', '0001_initial'),
        ('operador', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ostype',
            name='creator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ostype_ostype_creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ostype',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operador.operator'),
        ),
        migrations.AddField(
            model_name='ostype',
            name='updater',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ostype_ostype_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalostype',
            name='creator',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalostype',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalostype',
            name='operator',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operador.operator'),
        ),
        migrations.AddField(
            model_name='historicalostype',
            name='updater',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
