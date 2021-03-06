# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-06 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0004_auto_20180822_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academico',
            name='acreditacion',
            field=models.CharField(choices=[(b'candidato', b'candidato'), (b'no acreditado', b'no acreditado'), (b'D', b'D'), (b'M', b'M'), (b'E', b'E')], max_length=15),
        ),
        migrations.AlterField(
            model_name='academico',
            name='lineas',
            field=models.TextField(blank=True, verbose_name=b'Temas de inter\xc3\xa9s y/o experiencia en ciencias de la sostenibilidad, m\xc3\xa1ximo 10, uno por rengl\xc3\xb3n'),
        ),
        migrations.AlterField(
            model_name='academico',
            name='motivacion',
            field=models.TextField(blank=True, verbose_name=b'Motivaci\xc3\xb3n para participar en el Programa, m\xc3\xa1ximo 200 palabras'),
        ),
        migrations.AlterField(
            model_name='academico',
            name='palabras_clave',
            field=models.TextField(blank=True, verbose_name=b'Palabras clave de temas de inter\xc3\xa9s y/o experienciaen ciencias de la sostenibilidad, m\xc3\xa1ximo 10, una por rengl\xc3\xb3n'),
        ),
        migrations.AlterField(
            model_name='academico',
            name='participacion_comite_doctorado',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Cantidad de participaciones como miembro de comit\xc3\xa9 tutor (no tutor principal) en el PCS a nivel doctorado'),
        ),
        migrations.AlterField(
            model_name='academico',
            name='participacion_comite_maestria',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Cantidad de participaciones como miembro de comit\xc3\xa9 tutor (no tutor principal) en el PCS a nivel maestr\xc3\xada'),
        ),
        migrations.AlterField(
            model_name='academico',
            name='proyectos_sostenibilidad',
            field=models.TextField(blank=True, verbose_name=b'Principales proyectos relacionados con ciencias de la sostenibilidad durante los \xc3\xbaltimos cinco a\xc3\xb1os, especificar si se es responsable o colaborador.'),
        ),
    ]
