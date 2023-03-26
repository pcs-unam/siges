# Generated by Django 3.2.15 on 2023-03-17 20:03

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0124_alter_invitadomembresiacomite_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graduado',
            name='fecha',
            field=models.DateField(default=datetime.date.today, verbose_name='fecha de graduación'),
        ),
        migrations.AlterField(
            model_name='historial',
            name='fecha',
            field=models.DateField(default=datetime.date.today, help_text='fecha del registro en la bitácora', verbose_name='fecha del registro'),
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(choices=[('Maestría', 'Maestría'), ('Doctorado', 'Doctorado')], max_length=20)),
                ('sede', models.CharField(choices=[('CDMX', 'CDMX'), ('León', 'León'), ('Morelia (IIES)', 'Morelia (IIES)'), ('Morelia (ENES)', 'Morelia (ENES)')], max_length=20)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sedes', to='posgradmin.estudiante')),
            ],
            options={
                'verbose_name_plural': 'Sedes de estudiante',
                'unique_together': {('sede', 'plan')},
            },
        ),
    ]