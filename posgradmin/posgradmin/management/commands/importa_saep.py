# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
from pyexcel_ods3 import get_data


class Command(BaseCommand):
    help = u'Importa base de datos de SAEP'

    def add_arguments(self, parser):
        parser.add_argument('ods_file',
                            type=argparse.FileType('r'),
                            help='path al archivo en formato ods')

    def handle(self, *args, **options):
        importa(options['ods_file'])


def importa(db_file):
    data = get_data(db_file.name)

    for i in range(0, len(data['alumnos'])):
        a = data['alumnos'][i]

        if i == 0:
            idx = {f: a.index(f)
                   for f in a}
            continue
        elif len(a) == 0:
            continue
        elif a[idx['email']] == '':
            print(i, a[idx['cuenta']], 'sin email, imposible importar')
            continue
        
        # ['anio', 'semestre', 'cuenta', 'nombre', 'apellidop', 'apellidom', 'nombrew', 'edocivil', 'direccion', 'colonia', 'delegacion', 'estadores', 'codigo',
        # 'ladapart', 'telpart',
        # 'ladatrab', 'teltrab', 'exttrab', 
        # 'nacional', 'sexo', 'anio', 'mes', 'dia', 'carrera', 'facultad', 'institu', 'pais', 'estado', 'promedio', 'aniot', 'mest', 'diat', 'anioing', 'seming', 'ingrein', 'entidad', 'plan', 'orienta', 'tiempocp', 'email', 'curp', 'planpostant', 'facantpos', 'instantpos', 'paisantpos', 'estadoantpos', 'concluyoantpos', 'anogrant', 'mesgrant', 'diagrant']
        
        if models.User.objects.filter(username=a[idx['cuenta']]).count() == 1:
            u = models.User.objects.get(username=a[idx['cuenta']])
            if models.User.objects.filter(username=a[idx['email']].split('@')[0]).count() == 1:
                u.delete()
                print('pero ya existia con username, borrado', u.email.split('@')[0])
            else:
                u.username = u.email.split('@')[0]
                u.save()
                print('renamed', u)
        elif models.User.objects.filter(username=a[idx['email']].split('@')[0]).count() == 1:
            u = models.User.objects.get(username=a[idx['email']].split('@')[0])
            u.first_name = a[idx['nombrew']]
            u.last_name = a[idx['apellidop']] + " " + a[idx['apellidom']]
            u.email = a[idx['email']]
            u.save()
            print('updated', u)
        else:
            u, created = models.User.objects.get_or_create(
                username = a[idx['email']].split('@')[0],
                first_name = a[idx['nombrew']],
                last_name = a[idx['apellidop']] + " " + a[idx['apellidom']],
                email = a[idx['email']]
            )

            if created:
                print('created', u)
            else:
                print('weird updated', u)

        # 'ladapart', 'telpart',                
        p, created = models.Perfil.objects.get_or_create(
            user = u)

        p.curp = a[idx['curp']],
        p.telefono = str(a[idx['ladapart']]) + str(a[idx['telpart']]),
        p.direccion1 = "\n".join([a[idx['direccion']],
                                  a[idx['colonia']],
                                  a[idx['delegacion']],
                                  a[idx['estadores']]])
        p.codigo_postal = a[idx['codigo']]
        p.genero = a[idx['sexo']]
        p.nacionalidad = a[idx['nacional']]
        p.fecha_nacimiento = datetime(a[idx['anio']],
                                      a[idx['mes']],
                                      a[idx['dia']])

        p.save()
        if created:
            print('creado perfil', p)
        else:
            print('update perfil', p)

