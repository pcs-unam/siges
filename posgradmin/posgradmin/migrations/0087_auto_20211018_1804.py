# Generated by Django 3.0.6 on 2021-10-18 23:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0086_auto_20211018_1752'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historial',
            options={'ordering': ['fecha'], 'verbose_name_plural': 'Historial'},
        ),
        migrations.RemoveField(
            model_name='historial',
            name='ingreso',
        ),
        migrations.RemoveField(
            model_name='historial',
            name='ultimo_estado',
        ),
        migrations.AddField(
            model_name='historial',
            name='estado',
            field=models.CharField(choices=[('inscrito', 'inscrito'), ('egresado', 'egresado'), ('graduado', 'graduado'), ('indeterminado', 'indeterminado'), ('baja', 'baja'), ('suspensión 1 sem', 'suspensión 1 sem'), ('suspensión 2 sem', 'suspensión 2 sem'), ('plazo adicional', 'plazo adicional')], default='inscrito', max_length=25),
        ),
        migrations.AddField(
            model_name='historial',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='historial',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='año'),
        ),
        migrations.AlterField(
            model_name='historial',
            name='semestre',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2)], verbose_name='semestre'),
        ),
        migrations.DeleteModel(
            name='EstadoHistorial',
        ),
    ]
