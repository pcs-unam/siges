# Generated by Django 3.0.6 on 2021-10-18 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0085_auto_20211018_1654'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estadohistorial',
            options={'ordering': ['fecha'], 'verbose_name_plural': 'estados de historial'},
        ),
        migrations.AlterModelOptions(
            name='historial',
            options={'ordering': ['ingreso'], 'verbose_name_plural': 'Historial'},
        ),
        migrations.AddField(
            model_name='historial',
            name='beca_descripcion',
            field=models.CharField(blank=True, max_length=200, verbose_name='Descripción de Beca'),
        ),
        migrations.AlterField(
            model_name='historial',
            name='beca',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='historial',
            name='estudiante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='posgradmin.Estudiante'),
        ),
        migrations.DeleteModel(
            name='Beca',
        ),
    ]
