# Generated by Django 3.2.15 on 2023-03-10 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0122_alter_academico_acreditacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acreditacion',
            name='acreditacion',
            field=models.CharField(choices=[('candidato', 'candidato'), ('candidato profesor', 'candidato profesor'), ('no acreditado', 'no acreditado'), ('información incompleta', 'información incompleta'), ('por reacreditar D', 'por reacreditar D'), ('por reacreditar M', 'por reacreditar M'), ('baja', 'baja'), ('condicionado', 'condicionado'), ('P', 'P'), ('D', 'D'), ('M', 'M'), ('MCT_M', 'MCT_M'), ('E', 'E')], default='candidato', max_length=25),
        ),
    ]
