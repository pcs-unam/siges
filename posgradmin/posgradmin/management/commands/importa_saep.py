# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
from pyexcel_ods3 import get_data


class Command(BaseCommand):
    help = u'Importa base de datos de SAEP, este script debe correr una sola vez!'

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

    # quitar usuarios con estudiante
    for u in models.User.objects.all():
        if hasattr( u, 'estudiante'):
            u.delete()
    # no debe haber usuarios que no sean estudiantes ni académicos
    for u in models.User.objects.all():
        if not hasattr( u, 'academico'):
            u.delete()

    # examinar el archivo linea por linea
    for i in range(0, len(data['alumnos'])):
        a = data['alumnos'][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: a.index(f)
                   for f in a}
            continue
        elif len(a) == 0:
            # descartar lineas vacias
            continue
        elif a[idx['email']] == '':
            # descartar estudiantes sin correo
            print('[ERROR] fila',i, 'cuenta', a[idx['cuenta']], 'sin email, imposible importar')
            continue


        u, created = models.User.objects.get_or_create(
            username = a[idx['email']].split('@')[0],
        )

        if created:
            u.last_name = " ".join([chunk.capitalize()
                                  for chunk in a[idx['apellidop']].split(" ")])
            u.last_name += " "
            u.last_name += " ".join([chunk.capitalize()
                                   for chunk in a[idx['apellidom']].split(" ")])

            u.first_name = " ".join([chunk.capitalize() for chunk in a[idx['nombrew']].split(" ")])

            u.email = a[idx['email']]
            u.save()
            print('nuevo usuario', u)

        p, created = models.Perfil.objects.get_or_create(user = u)
        if created:
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
            print('nuevo perfil', p)


        e, created = models.Estudiante.objects.get_or_create(
            user=u,
            cuenta=a[idx['cuenta']])

        if created:
            print("nuevo estudiante", e)

        if a[idx['plan']] == 5172:
            plan = 'Doctorado'
        elif a[idx['plan']] == 4172:
            plan = u'Maestría'
        else:
            plan = u'Maestría'

        h, created = models.Historial.objects.get_or_create(
            fecha=date(a[0], 8, 1),  # inscripciones en agosto, ver #223
            estudiante = e,
            year = a[0],
            plan = plan,
            estado = 'inscrito',
            semestre = a[idx['semestre']]
        )

        if not created:
            print('historial repetido', h)

        h.institucion = get_institucion(a[idx['entidad']])
        h.save()

        e.estado = e.ultimo_estado()
        e.plan = e.ultimo_plan()
        e.save()
