# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-20 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0031_curso_activo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignatura',
            name='asignatura',
            field=models.CharField(max_length=200),
        ),
    ]
