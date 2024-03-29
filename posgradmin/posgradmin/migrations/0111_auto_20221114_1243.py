# Generated by Django 3.2.15 on 2022-11-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0110_auto_20221114_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudiante',
            name='estado',
            field=models.CharField(blank=True, choices=[('inscrito', 'inscrito'), ('egresado', 'egresado'), ('graduado', 'graduado'), ('indeterminado', 'indeterminado'), ('baja', 'baja'), ('suspensión 1 sem', 'suspensión 1 sem'), ('suspensión 2 sem', 'suspensión 2 sem'), ('ausente', 'ausente')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='historial',
            name='estado',
            field=models.CharField(choices=[('inscrito', 'inscrito'), ('egresado', 'egresado'), ('graduado', 'graduado'), ('indeterminado', 'indeterminado'), ('baja', 'baja'), ('suspensión 1 sem', 'suspensión 1 sem'), ('suspensión 2 sem', 'suspensión 2 sem'), ('ausente', 'ausente')], default='inscrito', max_length=25),
        ),
    ]
