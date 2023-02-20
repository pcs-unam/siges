from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
from pyexcel_ods3 import get_data


class Command(BaseCommand):
    help = u'Importa proyectos de estudiantes, ver #278'

    def add_arguments(self, parser):
        parser.add_argument('ods_file',
                            type=argparse.FileType('r'),
                            help='path al archivo en formato ods')

    def handle(self, *args, **options):
        importa(options['ods_file'])


idx = {
    'anio': 0,
    'semestre': 1,
    'cuenta': 2,
    'nombre': 3,
}


def busca_estudiante(cuenta):
    return models.Estudiante.objects.filter(cuenta=cuenta).first()


def importa(db_file):
    data = get_data(db_file.name)

    for i in range(0, len(data['proyecto'])):
        row = data['proyecto'][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: row.index(f)
                   for f in row}
            continue
        elif len(row) == 0:
            # descartar lineas vacias
            continue


        # anio	semestre	cuenta	nombre
        estudiante = busca_estudiante(row[idx['cuenta']])
        titulo = row[idx['nombre']]
        
        if (estudiante
            and not 'defini' in titulo.lower()   # para omitir "proyecto no definido o sin definir"
            and models.Proyecto.objects.filter(estudiante=estudiante).filter(titulo=titulo).count() == 0):   # no repetir titulos
            
            if row[idx['semestre']] == 1:
                fecha = date(row[idx['anio']], 8, 1)
            elif row[idx['semestre']] == 2:
                fecha = date(row[idx['anio']], 1, 1)
                
            p = models.Proyecto(estudiante=estudiante,
                                fecha=fecha,
                                titulo=titulo)
            p.save()

            print('proyecto nuevo', p)

