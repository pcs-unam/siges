# Generated by Django 3.0.6 on 2021-09-30 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0080_auto_20210930_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudiante',
            name='promedio_ingreso',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=2, verbose_name='Promedio del último grado. Dos dígitos máximo, dos decimales.'),
            preserve_default=False,
        ),
    ]
