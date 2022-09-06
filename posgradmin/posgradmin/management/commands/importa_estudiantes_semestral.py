# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
import csv
import jellyfish

class Command(BaseCommand):
    help = u'Importa base de datos de DGAE y SAEP'

    def add_arguments(self, parser):
        parser.add_argument('--dgae',
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo DGAE en formato csv')
        """ folio,campo_conocimiento_seleccionado,entidad_academica_seleccionada,modalidad_seleccionada,tiempo_dedicacion,apellido1,apellido2,nombre,fecha_nacimiento,genero,curp,nacionalidad,estado_civil,pais_telefono,telefono,pais_celular,celular,correo,direccion,orientacion_interdisciplinaria,estatus_orientacion_interdisciplinaria,documentos_personales,documentos_administrativos,documentos_academicos """


        parser.add_argument('--saep',
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo SAEP en formato csv')


    def handle(self, *args, **options):

        importa(options['dgae'], options['saep'])


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



def importa(dgae, saep):
    saepr = csv.DictReader(saep)
    dgaer = csv.DictReader(dgae)

    # leemos saep y separamos ingresos de reingresos
    reingresos = []
    nuevos_saep = {}
    for row in saepr:
        # usamos la pronunciacion del nombre como llave, para unir SAEP con DGAE
        metaphone = jellyfish.metaphone("%s %s %s" % (row['nombre'],
                                                      row['apellido1'],
                                                      row['apellido2']))

        if row['inscripcion'] == 'REINGRESO':
            reingresos.append(row)
        elif row['inscripcion'] == 'INGRESO':
            nuevos_saep[metaphone] = row


    folio_dgae = {}
    dgae = []
    for row in dgaer:
        metaphone = jellyfish.metaphone("%s %s %s" % (row['nombre'],
                                                      row['apellido1'],
                                                      row['apellido2']))
        # este diccionario permite unir folio en DGAE con cuenta en SAEP
        folio_dgae[metaphone] = row['folio']
        dgae.append(row)


    # DGAE repite renglones por estudiante, por cada grado academico
    # a continuacion generamos una lista y la guardamos en un diccionario
    # con el folio DGAE como llave
    campos_grado = ["antecedente_academico", "nivel_antecedente_academico", "promedio",
                    "estatus_graduacion", "fecha_graduacion", "entidad_academica",
                    "institucion", "pais_antecedente_academico",
                    "antecedente_academico_ingreso", "estado_antecedente_academico",
                    "completa", "completada_en_fecha"]

    grados_dgae = {}
    for a in dgae:
        folio = a['folio']

        grado = {}
        for c in campos_grado:
            grado[c] = a[c]

        if folio in grados_dgae:
            grados_dgae[folio].append(grado)
        else:
            grados_dgae[folio] = [grado, ]


    # por otro lado hacemos un diccionario de alumnos DGAE
    # cuya llave es el folio DGAE
    alumno_dgae = {}
    for a in dgae:
        folio = a['folio']
        # tirar todo lo que se repite
        for c in campos_grado + ['folio',
                                 'orientacion_interdisciplinaria',
                                 'estatus_orientacion_interdisciplinaria',
                                 'documentos_personales',
                                 'documentos_administrativos',
                                 'documentos_academicos']:
            a.pop(c)

            alumno_dgae[folio] = a


    # Cargar todos los alumnos nuevos a la base de datos
    for n in nuevos_saep:
        print(nuevos_saep[n]['cuenta'], alumno_dgae[folio_dgae[n]], len(grados_dgae[folio_dgae[n]]))

                                 # for n in nuevos_saep:
                                 #     print(nuevos_saep[n]['cuenta'], nuevos_dgae[n])
                                 #     a = nuevos_saep[n]
                                 #     u, created = models.User.objects.get_or_create(
                                 #         username = a['email'].split('@')[0],
                                 #         first_name = ""
                                 #         last_name = ""
                                 #         email = ""
                                 #     )

                                 #     if created:
                                 #         print('created', u)

                                 #     p, created = models.Perfil.objects.get_or_create(user = u)
                                 #     p.curp = a[idx['curp']]
                                 #     p.telefono = str(a[idx['ladapart']]) + str(a[idx['telpart']])
                                 #     p.direccion1 = "\n".join([a[idx['direccion']],
                                 #                               a[idx['colonia']],
                                 #                               a[idx['delegacion']],
                                 #                               a[idx['estadores']]])
                                 #     p.codigo_postal = a[idx['codigo']]
                                 #     p.genero = a[idx['sexo']]
                                 #     p.nacionalidad = a[idx['nacional']]
                                 #     p.fecha_nacimiento = datetime(a[20],
                                 #                                   a[idx['mes']],
                                 #                                   a[idx['dia']])

                                 #     p.save()
                                 #     if created:
                                 #         print('creado perfil', p)
                                 #     else:
                                 #         print('update perfil', p)





                                 #     if models.User.objects.filter(username=a[idx['cuenta']]).count() == 1:
                                 #         u = models.User.objects.get(username=a[idx['cuenta']])
                                 #         if models.User.objects.filter(username=a[idx['email']].split('@')[0]).count() == 1:
                                 #             u.delete()
                                 #             print('pero ya existia con username, borrado', u.email.split('@')[0])
                                 #         else:
                                 #             u.username = u.email.split('@')[0]
                                 #             u.save()
                                 #             print('renamed', u)
                                 #     elif models.User.objects.filter(username=a[idx['email']].split('@')[0]).count() == 1:
                                 #         u = models.User.objects.get(username=a[idx['email']].split('@')[0])
                                 #         print('loaded', u)
                                 #     else:
                                 #         u, created = models.User.objects.get_or_create(
                                 #             username = a[idx['email']].split('@')[0],
                                 #             first_name = " ".join([chunk.capitalize() for chunk in a[idx['nombrew']].split(" ")]),
                                 #             last_name = " ".join([chunk.capitalize()
                                 #                                   for chunk in a[idx['apellidop']].split(" ")]) \
                                 #                             + " " \
                                 #                             + \
                                 #                             " ".join([chunk.capitalize()
                                 #                                       for chunk in a[idx['apellidom']].split(" ")]),
                                 #             email = a[idx['email']]
                                 #         )

                                 #         if created:
                                 #             print('created', u)

                                 #     u.first_name = " ".join([chunk.capitalize()
                                 #                              for chunk in a[idx['nombrew']].split(" ")])
                                 #     u.last_name = " ".join([chunk.capitalize()
                                 #                             for chunk in a[idx['apellidop']].split(" ")]) \
                                 #                                 + " " \
                                 #                                 + \
                                 #                                 " ".join([chunk.capitalize()
                                 #                                           for chunk in a[idx['apellidom']].split(" ")])
                                 #     u.email = a[idx['email']]
                                 #     u.save()
                                 #     print('updated', u)

                                 #     p, created = models.Perfil.objects.get_or_create(user = u)
                                 #     p.curp = a[idx['curp']]
                                 #     p.telefono = str(a[idx['ladapart']]) + str(a[idx['telpart']])
                                 #     p.direccion1 = "\n".join([a[idx['direccion']],
                                 #                               a[idx['colonia']],
                                 #                               a[idx['delegacion']],
                                 #                               a[idx['estadores']]])
                                 #     p.codigo_postal = a[idx['codigo']]
                                 #     p.genero = a[idx['sexo']]
                                 #     p.nacionalidad = a[idx['nacional']]
                                 #     p.fecha_nacimiento = datetime(a[20],
                                 #                                   a[idx['mes']],
                                 #                                   a[idx['dia']])

                                 #     p.save()
                                 #     if created:
                                 #         print('creado perfil', p)
                                 #     else:
                                 #         print('update perfil', p)


                                 #     if models.Estudiante.objects.filter(user = u).count() > 0:
                                 #         e = models.Estudiante.objects.get(user=u)
                                 #         e.cuenta = a[idx['cuenta']]
                                 #         e.promedio_ingreso = 10.0
                                 #         e.save()
                                 #     else:
                                 #         e = models.Estudiante(
                                 #             user=u,
                                 #             cuenta=a[idx['cuenta']],
                                 #             promedio_ingreso = 10.0)
                                 #         e.save()

                                 #     if created:
                                 #         print('created estudiante', e)
                                 #     else:
                                 #         print('updated estudiante', e)

                                 #     print('found estudiante', models.Estudiante.objects.filter(cuenta=a[idx['cuenta']]).count())


                                 #     if a[idx['plan']] == 5172:
                                 #         plan = 'Doctorado'
                                 #     elif a[idx['plan']] == 4172:
                                 #         plan = u'Maestría'
                                 #     else:
                                 #         plan = u'Maestría'

                                 #     if models.Historial.objects.filter(estudiante=e, plan=plan,
                                 #                                        estado='inscrito').count() == 0:
                                 #         h, created = models.Historial.objects.get_or_create(
                                 #             fecha=date(a[0], 8, 1),  # inscripciones en agosto, ver #223
                                 #             estudiante = e,
                                 #             year = a[0],
                                 #             plan = plan,
                                 #             estado = 'inscrito',
                                 #             semestre = a[idx['semestre']]
                                 #         )

                                 #     h.institucion = get_institucion(a[idx['entidad']])
                                 #     h.save()

                                 #     if created:
                                 #         print('created estudios', h)
                                 #     else:
                                 #         print('updated estudios', h)
