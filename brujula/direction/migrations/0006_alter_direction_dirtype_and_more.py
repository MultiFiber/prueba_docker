# Generated by Django 4.0.5 on 2023-02-23 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direction', '0005_direction_full_direction_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='direction',
            name='dirtype',
            field=models.IntegerField(choices=[(0, 'País'), (1, 'Region'), (2, 'Estado'), (3, 'Municipio'), (4, 'Parroquia'), (5, 'Comuna'), (6, 'Distrito'), (7, 'Calle'), (8, 'Avenida'), (9, 'Cuadra'), (10, 'Carretera'), (11, 'Diagonal'), (12, 'Transversal'), (13, 'locacion calle'), (14, 'Continente'), (15, 'Quinta'), (16, 'Torre'), (17, 'Piso'), (18, 'Locacion completa'), (19, 'Manzana'), (20, 'lote'), (20, 'poblado')]),
        ),
        migrations.AlterField(
            model_name='historicaldirection',
            name='dirtype',
            field=models.IntegerField(choices=[(0, 'País'), (1, 'Region'), (2, 'Estado'), (3, 'Municipio'), (4, 'Parroquia'), (5, 'Comuna'), (6, 'Distrito'), (7, 'Calle'), (8, 'Avenida'), (9, 'Cuadra'), (10, 'Carretera'), (11, 'Diagonal'), (12, 'Transversal'), (13, 'locacion calle'), (14, 'Continente'), (15, 'Quinta'), (16, 'Torre'), (17, 'Piso'), (18, 'Locacion completa'), (19, 'Manzana'), (20, 'lote'), (20, 'poblado')]),
        ),
    ]
