# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-21 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0027_auto_20190221_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='academico',
            name='fecha_acreditacion',
            field=models.DateField(blank=True, null=True),
        ),
    ]
