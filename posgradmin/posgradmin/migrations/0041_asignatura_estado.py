# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-11-21 04:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0040_auto_20191120_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignatura',
            name='estado',
            field=models.CharField(choices=[('nueva', b'nueva'), ('aceptada', 'aceptada')], default=b'nueva', max_length=40),
        ),
    ]