# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-02-06 01:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0053_auto_20200205_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acreditacion',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
