# Generated by Django 3.0.6 on 2021-09-30 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0078_auto_20210622_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudios',
            name='beca',
            field=models.CharField(blank=True, max_length=200, verbose_name='Descripción de Beca'),
        ),
        migrations.AddField(
            model_name='estudios',
            name='permiso_trabajar',
            field=models.BooleanField(default=False),
        ),
    ]
