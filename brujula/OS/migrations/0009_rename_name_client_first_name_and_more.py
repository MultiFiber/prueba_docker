# Generated by Django 4.0.5 on 2023-02-22 17:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('operador', '0004_alter_historicaloperator_operator_code_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('OS', '0008_merge_20230222_1206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='historicalclient',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='historicalos',
            old_name='plan',
            new_name='plan_id',
        ),
        migrations.RenameField(
            model_name='os',
            old_name='plan',
            new_name='plan_id',
        ),
        migrations.RemoveField(
            model_name='client',
            name='dni',
        ),
        migrations.RemoveField(
            model_name='historicalclient',
            name='dni',
        ),
        migrations.AddField(
            model_name='client',
            name='direction_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='document_number',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='document_type',
            field=models.SmallIntegerField(choices=[(0, 'DNI'), (1, 'RUT'), (2, 'RUC')], default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalclient',
            name='direction_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalclient',
            name='document_number',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalclient',
            name='document_type',
            field=models.SmallIntegerField(choices=[(0, 'DNI'), (1, 'RUT'), (2, 'RUC')], default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalos',
            name='user_brujula',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='OS.client'),
        ),
        migrations.AddField(
            model_name='os',
            name='user_brujula',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='OS.client'),
        ),
        migrations.CreateModel(
            name='OperatorPlans',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('tradename', models.CharField(max_length=255)),
                ('technology', models.CharField(blank=True, max_length=100, null=True)),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creator', to=settings.AUTH_USER_MODEL)),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operador.operator')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updater', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Plan del operador',
                'verbose_name_plural': 'Planes de operador',
            },
        ),
        migrations.CreateModel(
            name='HistoricalOperatorPlans',
            fields=[
                ('ID', models.IntegerField(blank=True, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, editable=False)),
                ('tradename', models.CharField(max_length=255)),
                ('technology', models.CharField(blank=True, max_length=100, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('creator', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('operator', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operador.operator')),
                ('updater', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Plan del operador',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name='historicalos',
            name='plan_brujula',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='OS.operatorplans'),
        ),
        migrations.AddField(
            model_name='os',
            name='plan_brujula',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='OS.operatorplans'),
        ),
    ]
