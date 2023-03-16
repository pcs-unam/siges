# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
from pyexcel_ods3 import get_data


class Command(BaseCommand):
    help = u'Rescata perfiles de alumnos que venían right-shifted.'

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
    # for u in models.User.objects.all():
    #     if hasattr( u, 'estudiante'):
    #         u.delete()
    # no debe haber usuarios que no sean estudiantes ni académicos
    # for u in models.User.objects.all():
    #     if not hasattr( u, 'academico'):
    #         u.delete()


    purged = []
    # examinar el archivo linea por linea
    for i in range(0, len(data['alumni'])):
        a = data['alumni'][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: a.index(f)
                   for f in a}
            continue
        elif len(a) == 0:
            # descartar lineas vacias
            continue
        elif a[idx['correos']] == '':
            # descartar estudiantes sin correo
            print('[ERROR] fila',i, 'cuenta', a[idx['cuenta']], 'sin email, imposible importar')
            continue

        correos = a[idx['correos']].split(',')
        username = correos[0].split('@')[0]

        cuenta=a[idx['cuenta']]
        e_hallados = models.Estudiante.objects.filter(cuenta=cuenta).count()        
        if e_hallados == 1:
            # estudiante existe!
            print(f'Estudiante existe: {cuenta}')
            e = models.Estudiante.objects.get(cuenta=cuenta)
            u = e.user
            if models.User.objects.filter(username=username).count == 0:            
                u.username = username
                u.save()
            e_created = False
            u_created = False
            print(f'usuario actualizado {u}')
        elif e_hallados > 1:
            print(f'Mas de un estudiante con esta cuenta: {cuenta}')
            e = models.Estudiante.objects.filter(cuenta=cuenta).last()
            print(f'eligiendo el último {e}')
            u = e.user
            if models.User.objects.filter(username=username).count == 0:
                u.username = username
                u.save()
            
            e_created = False
            u_created = False
            print(f'usuario actualizado {u}')
            
        else:
            # estudiante no existe!
            print(f'Estudiante no existe: {cuenta}')
            u, u_created = models.User.objects.get_or_create(
                username=username
            )
            if u_created:
                print(f'Usuario creado: {u}')
            else:
                print(f'Usuario existe: {u}')
                
            e, e_created = models.Estudiante.objects.get_or_create(
                user=u,
                cuenta=a[idx['cuenta']])
            print(f"estudiante creado: {e}")
            
        u.last_name = " ".join([chunk.capitalize()
                                for chunk in a[idx['primer_apellido']].split(" ")])
        u.last_name += " "
        u.last_name += " ".join([chunk.capitalize()
                                 for chunk in a[idx['segundo_apellido']].split(" ")])

        u.first_name = " ".join([chunk.capitalize() for chunk in a[idx['nombre']].split(" ")])

        u.email = correos[0]
        u.save()
        print(f'usuario actualizado {u}')

        
        p, created = models.Perfil.objects.get_or_create(user = u)
        if created:
            print(f"perfil creado: {p}")
        else:
            print(f"perfil encontrado: {p}")

        # filas sin curp a veces estan truncadas, siempre son extranjeres
        if len(a) > 34:
            try:
                p.curp = a[idx['curp']]
            except:
                print(a, len(a), idx)
                exit()
        else:
            p.curp = 'extranjere'
        
        p.telefono = str(str(a[idx['tel_1']]))
        p.direccion1 = "\n".join([str(a[idx['calle_numero']]),
                                  a[idx['colonia']],
                                  a[idx['delegacion']],
                                  a[idx['entidad_federativa']]])
        p.codigo_postal = a[idx['codigo_postal']]
        p.genero = a[idx['genero']]
        p.nacionalidad = a[idx['nacionalidad']]

        p.fecha_nacimiento = a[idx['fecha_nacimiento']]

        p.save()
        print(f'perfil actualizado: {p}')

        # eliminar historial del estudiante
        if not e in purged:
            for h in e.historial.all():
                h.delete()
            purged.append(e)
            print('historial purgado para ', e)
        
        if a[idx['plan']] == 5172:
            plan = 'Doctorado'
        elif a[idx['plan']] == 4172:
            plan = u'Maestría'
        else:
            plan = u'Maestría'

        h, h_created = models.Historial.objects.get_or_create(
            fecha=date(a[idx['anio']], 8, 1),  # inscripciones en agosto, ver #223
            estudiante = e,
            year = a[idx['anio']],
            plan = plan,
            estado = 'inscrito',
            semestre = a[idx['semestre']]
        )

        if h_created:
            print('historial importado', h)
        else:
            print('historial repetido', h)

        h.institucion = get_institucion(a[idx['entidad']])
        h.save()

        e.estado = e.ultimo_estado()
        e.plan = e.ultimo_plan()
        e.save()
