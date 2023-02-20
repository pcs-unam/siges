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



lineas = {
    (5172, 1): 1,
    (5172, 2): 2,
    (5172, 3): 3,
    (5172, 4): 4,
    (5172, 5): 5,
    (5172, 6): 6,
    (5172, 7): 7
}

campos = {
    (4172, 1): 18,
    (4172, 2): 19,
    (4172, 3): 20,
    (4172, 4): 21,
    (4172, 5): 22,
    (4172, 6): 23
}


def busca_estudiante(cuenta):
    return models.Estudiante.objects.filter(cuenta=cuenta).first()


def importa(db_file):
    data = get_data(db_file.name)

    for i in range(0, len(data['alumnos'])):
        row = data['alumnos'][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: row.index(f)
                   for f in row}
            continue
        elif len(row) == 0:
            # descartar lineas vacias
            continue

        #print(idx)
        #exit(0)
        
        estudiante = busca_estudiante(row[idx['cuenta']])
        
        if estudiante:
            if type(row[idx['promedio']]) == str:    # renglones deformes
                orienta = row[idx['type']]
                plan = row[idx['orienta']]                
            else:
                orienta = row[idx['orienta']]
                plan = row[idx['plan']]

            if orienta == 0:
                continue
            
            if plan == 4172:
                campo = models.CampoConocimiento.objects.get(pk=campos[(plan, orienta)])
                estudiante.campo_conocimiento = campo
                estudiante.save()
                print(estudiante, campo)
            elif plan == 5172:
                linea = models.LineaInvestigacion.objects.get(pk=lineas[(plan, orienta)])
                estudiante.lineas_investigacion = linea
                estudiante.save()
                print(estudiante, linea)
                

