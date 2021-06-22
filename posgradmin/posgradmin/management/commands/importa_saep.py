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


def get_institucion(entidad_num):
    if entidad_num == 600:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Escuela Nacional de Estudios Superiores Unidad León",
                                              entidad_PCS=True)
    if entidad_num == 700:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Escuela Nacional de Estudios Superiores Unidad Morelia",
                                              entidad_PCS=True)
    if entidad_num == 1:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Facultad de Arquitectura ",
                                              entidad_PCS=True)
    if entidad_num == 3:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Facultad de Ciencias",
                                              entidad_PCS=True)
    if entidad_num == 65:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Biología",
                                              entidad_PCS=True)
    if entidad_num == 67:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Ciencias del Mar y Limnología",
                                              entidad_PCS=True)
    if entidad_num == 69:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Ecología",
                                              entidad_PCS=True)
    if entidad_num == 90:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Energías Renovables",
                                              entidad_PCS=True)
    if entidad_num == 11:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Ingeniería",
                                              entidad_PCS=True)
    if entidad_num == 79:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Investigaciones Económicas",
                                              entidad_PCS=True)
    if entidad_num == 87:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Investigaciones Sociales",
                                              entidad_PCS=True)
    if entidad_num == 97:
        return models.Institucion.objects.get(nombre="Universidad Nacional Autónoma de México",
                                              suborganizacion="Instituto de Investigaciones en Ecosistemas y Sustentabilidad",
                                              entidad_PCS=True)

        

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

        # anio	semestre	cuenta	nombre	apellidop	apellidom	nombrew	edocivil	direccion	colonia	delegacion	estadores	codigo	telpart	teltrab	exttrab	ladatrab	ladapart	nacional	sexo	anio	mes	dia	carrera	facultad	institu	pais	estado	promedio	aniot	mest	diat	anioing	seming	ingrein	entidad	plan	orienta	tiempocp	email	curp	planpostant	facantpos	instantpos	paisantpos	estadoantpos	concluyoantpos	anogrant	mesgrant	diagrant

        # ['anio', 'semestre', 'cuenta',
        # 'edocivil',
        # 'carrera', 'facultad', 'institu', 'pais', 'estado', 'promedio', 'aniot', 'mest', 'diat',
        #'anioing', 'seming', 'ingrein',
        # 'entidad', 'plan', 'orienta', 'tiempocp',
        # 'planpostant', 'facantpos', 'instantpos', 'paisantpos', 'estadoantpos', 'concluyoantpos', 'anogrant', 'mesgrant', 'diagrant']

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
            print('loaded', u)
        else:
            u, created = models.User.objects.get_or_create(
                username = a[idx['email']].split('@')[0],
                first_name = " ".join([chunk.capitalize() for chunk in a[idx['nombrew']].split(" ")]),
                last_name = " ".join([chunk.capitalize()
                                      for chunk in a[idx['apellidop']].split(" ")]) \
                                + " " \
                                + \
                                " ".join([chunk.capitalize()
                                          for chunk in a[idx['apellidom']].split(" ")]),
                email = a[idx['email']]
            )

            if created:
                print('created', u)

        u.first_name = " ".join([chunk.capitalize()
                                 for chunk in a[idx['nombrew']].split(" ")])
        u.last_name = " ".join([chunk.capitalize()
                                for chunk in a[idx['apellidop']].split(" ")]) \
                                    + " " \
                                    + \
                                    " ".join([chunk.capitalize()
                                              for chunk in a[idx['apellidom']].split(" ")])
        u.email = a[idx['email']]
        u.save()
        print('updated', u)
                
        p, created = models.Perfil.objects.get_or_create(user = u)
        p.curp = a[idx['curp']]
        p.telefono = str(a[idx['ladapart']]) + str(a[idx['telpart']])
        p.direccion1 = "\n".join([a[idx['direccion']],
                                  a[idx['colonia']],
                                  a[idx['delegacion']],
                                  a[idx['estadores']]])
        p.codigo_postal = a[idx['codigo']]
        p.genero = a[idx['sexo']]
        p.nacionalidad = a[idx['nacional']]
        p.fecha_nacimiento = datetime(a[20],
                                      a[idx['mes']],
                                      a[idx['dia']])

        p.save()
        if created:
            print('creado perfil', p)
        else:
            print('update perfil', p)


        e, created = models.Estudiante.objects.get_or_create(
            user = u
        )
        e.cuenta = a[idx['cuenta']]
        e.save()

        if created:
            print('created estudiante', e)
        else:
            print('updated estudiante', e)

        print('found estudiante', models.Estudiante.objects.filter(cuenta=a[idx['cuenta']]).count())


        s, created = models.Estudios.objects.get_or_create(
            estudiante = e,
            ingreso = a[0],
            semestre = a[idx['semestre']]
        )

        if a[idx['plan']] == 5172:
            s.plan = 'Doctorado'
        elif a[idx['plan']] == 4172:
            s.plan = u'Maestría'
        else:
            s.plan = u'Maestría'

        s.institucion = get_institucion(a[idx['entidad']])
        s.save()

        if created:
            print('created estudios', s)
        else:
            print('updated estudios', s)


