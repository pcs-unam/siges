# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
from pyexcel_ods3 import get_data


class Command(BaseCommand):
    help = u'Importa membresias de comites de SAEP'

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
    'rfc': 3,
    'tipo': 4,
}

tutor_curp = {}
tutor_email = {}


def busca_tutor(rfc):

    p = models.Perfil.objects.filter(rfc__icontains=rfc).first()

    if p:
        if  hasattr(p.user, 'academico'):
            return p.user.academico

    return None


def busca_estudiante(cuenta):
    return models.Estudiante.objects.filter(cuenta=cuenta).first()


def importa(db_file):
    data = get_data(db_file.name)


    for i in range(0, len(data['altutor'])):
        row = data['altutor'][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: row.index(f)
                   for f in row}
            continue
        elif len(row) == 0:
            # descartar lineas vacias
            continue


        # anio	semestre	cuenta	rfc	tipo
        tutor = busca_tutor(row[idx['rfc']])
        estudiante = busca_estudiante(row[idx['cuenta']])

        if tutor and estudiante:
            m, created = models.MembresiaComite.objects.get_or_create(
                estudiante=estudiante,
                tutor=tutor,
                year=row[idx['anio']],
                semestre=row[idx['semestre']],
                tipo=row[idx['tipo']])

            if created:
                print('membresia creada', m)
            else:
                print('membresia ya existente', m)

