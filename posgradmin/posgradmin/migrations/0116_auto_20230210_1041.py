# Generated by Django 3.2.15 on 2023-02-10 16:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0115_auto_20230210_1033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historial',
            name='folio_graduacion',
        ),
        migrations.RemoveField(
            model_name='historial',
            name='medalla_alfonso_caso',
        ),
        migrations.RemoveField(
            model_name='historial',
            name='mencion_honorifica',
        ),
        migrations.RemoveField(
            model_name='historial',
            name='modo_graduacion',
        ),
        migrations.CreateModel(
            name='Graduado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mencion_honorifica', models.BooleanField(default=False)),
                ('medalla_alfonso_caso', models.BooleanField(default=False, verbose_name='Medalla Alfonso Caso')),
                ('fecha', models.DateField(default=datetime.date.today)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='año')),
                ('semestre', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2)], verbose_name='semestre')),
                ('plan', models.CharField(choices=[('Maestría', 'Maestría'), ('Doctorado', 'Doctorado')], max_length=20)),
                ('folio_graduacion', models.CharField(blank=True, max_length=200, verbose_name='Folio de acta de examen de grado')),
                ('modo_graduacion', models.CharField(choices=[('-', '-'), ('tesis', 'tesis'), ('reporte técnico', 'reporte técnico'), ('artículo', 'artículo'), ('protocolo de investigación doctoral', 'protocolo de investigación doctoral')], default='-', max_length=35)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='graduaciones', to='posgradmin.estudiante')),
            ],
        ),
    ]
