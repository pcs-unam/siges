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


def importa(db_file):
    data = get_data(db_file.name)

    for i in range(0, len(data['altutor']) - 1):
        m = data['altutor'][i]
        if len(m) == 0:
            continue

        rfc_hits = models.Perfil.objects.filter(
            rfc__icontains=m[
                idx['rfc']
            ]
        ).count()

        if rfc_hits == 1:

            p = models.Perfil.objects.filter(rfc__icontains=m[idx['rfc']])[0]

            a = p.user.academico

            if models.Estudiante.objects.filter(cuenta=m[idx['cuenta']]).count() == 1:
                e = models.Estudiante.objects.get(cuenta=m[idx['cuenta']])

                mc, created = models.MembresiaComite.objects.get_or_create(
                    estudiante=e,
                    tutor=a,
                    year=m[idx['anio']],
                    semestre=m[idx['semestre']],
                    tipo=m[idx['tipo']])

                if created:
                    print('membresia creada', mc)
                else:
                    print('membresia ya existente', mc)

            elif models.Estudiante.objects.filter(cuenta=m[idx['cuenta']]).count() > 1:
                print('Estudiante DUPLICADO', m[idx['cuenta']])

        elif rfc_hits == 0:
            print('perfil no encontrado', m[idx['rfc']])

        elif rfc_hits > 1:
            print('perfil con rfc duplicado', m[idx['rfc']])
