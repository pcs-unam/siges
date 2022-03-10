# Generated by Django 3.2 on 2022-03-10 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0103_auto_20220223_1222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anexo',
            name='autor',
        ),
        migrations.RemoveField(
            model_name='anexo',
            name='solicitud',
        ),
        migrations.RemoveField(
            model_name='comentario',
            name='autor',
        ),
        migrations.RemoveField(
            model_name='comentario',
            name='solicitud',
        ),
        migrations.RemoveField(
            model_name='solicitud',
            name='sesion',
        ),
        migrations.RemoveField(
            model_name='solicitud',
            name='solicitante',
        ),
        migrations.RemoveField(
            model_name='academico',
            name='solicitud',
        ),
        migrations.DeleteModel(
            name='Acuerdo',
        ),
        migrations.DeleteModel(
            name='Anexo',
        ),
        migrations.DeleteModel(
            name='Comentario',
        ),
        migrations.DeleteModel(
            name='Solicitud',
        ),
    ]
