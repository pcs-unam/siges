# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-21 17:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0026_auto_20190221_1136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='academico',
            old_name='ultima_acreditacion',
            new_name='ultima_reacreditacion',
        ),
    ]
