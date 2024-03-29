# Generated by Django 3.2.15 on 2023-03-22 01:25

from django.db import migrations, models


def plan_from_year(apps, schema_editor):
    Proyecto = apps.get_model('posgradmin', 'Proyecto')
    for p in Proyecto.objects.all():
        e = p.estudiante
        h = e.historial.filter(year=p.fecha.year)
        if h.count() > 0:
            print('updating', p.plan)
            p.plan = h.first().plan
            p.save()
            print('set to', p.plan)
            


        

class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0126_auto_20230317_1406'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sede',
            options={'verbose_name_plural': 'Sedes administrativas'},
        ),
        migrations.AddField(
            model_name='proyecto',
            name='plan',
            field=models.CharField(choices=[('Maestría', 'Maestría'), ('Doctorado', 'Doctorado')], default='Maestría', max_length=20),
        ),
        migrations.RunPython(plan_from_year),
    ]
