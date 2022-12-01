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

    if models.Perfil.objects.filter(
            rfc__icontains=rfc
    ).count() == 1:
        p = models.Perfil.objects.filter(rfc__icontains=rfc)[0]
    elif models.Perfil.objects.filter(
            curp__icontains=tutor_curp.get(rfc, 'aguas')
    ).count() == 1:
        p = models.Perfil.objects.filter(curp__icontains=tutor_curp[rfc])[0]
    elif models.User.objects.filter(
            email__icontains=tutor_email.get(rfc, 'aguas@example.com')
    ).count() == 1:
        u = models.User.objects.filter(email__icontains=tutor_email[rfc])[0]
        if hasattr(u, 'perfil'):
            p = u.perfil
        else:
            return None
    else:
        print('nomas no encontre', rfc)
        return None
    return p.user.academico



def importa(db_file):
    data = get_data(db_file.name)

    models.MembresiaComite.objects.all().delete()

    # crea diccionario: llaves son rfc, valores curps y correos
    for i in range(0, len(data['tutor']) - 1):
        m = data['tutor'][i]
        if len(m) == 0:
            continue
        elif len(m) > 9:
            tutor_email[m[0]] = m[9]
        tutor_curp[m[0]] = m[8]

    # busca tutores por rfc
    for i in range(0, len(data['altutor']) - 1):
        m = data['altutor'][i]
        if len(m) == 0:
            continue

        print('busque', m[idx['rfc']], 'hallazgo', busca_tutor(m[idx['rfc']]))

        a = busca_tutor(m[idx['rfc']])

        if a is not None:

            if models.Estudiante.objects.filter(cuenta=m[idx['cuenta']]).count() == 1:
                e = models.Estudiante.objects.get(cuenta=m[idx['cuenta']])

                if models.MembresiaComite.objects.filter(
                        estudiante=e,
                        tutor=a,
                        year=m[idx['anio']],
                        semestre=m[idx['semestre']],
                        tipo=m[idx['tipo']]).count() == 0:
                    membresia = models.MembresiaComite(
                        estudiante=e,
                        tutor=a,
                        year=m[idx['anio']],
                        semestre=m[idx['semestre']],
                        tipo=m[idx['tipo']])
                    membresia.save()
                    print('membresia creada', membresia)
                else:
                    print('membresia ya existente', e, a)

            elif models.Estudiante.objects.filter(cuenta=m[idx['cuenta']]).count() > 1:
                print('Estudiante DUPLICADO', m[idx['cuenta']])
