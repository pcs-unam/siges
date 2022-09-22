# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
import csv
import jellyfish
from pprint import pprint

class Command(BaseCommand):
    help = u'Importa base de datos de DGAE y SAEP'

    def add_arguments(self, parser):
        parser.add_argument('--dgae',
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo DGAE en formato csv')

        parser.add_argument('--saep',
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo SAEP en formato csv')


    def handle(self, *args, **options):

        importa(options['dgae'], options['saep'])




def importa(dgae, saep):
    saepr = csv.DictReader(saep)
    dgaer = csv.DictReader(dgae)

    # leemos saep y separamos ingresos de reingresos
    reingresos = {}
    nuevos_saep = {}
    for row in saepr:
        # usamos la pronunciacion del nombre como llave, para unir SAEP con DGAE
        metaphone = jellyfish.metaphone("%s %s %s" % (row['nombre'],
                                                      row['apellido1'],
                                                      row['apellido2']))

        if row['inscripcion'] == 'REINGRESO':
            reingresos[metaphone] = row
        elif row['inscripcion'] == 'INGRESO':
            nuevos_saep[metaphone] = row


    idx_dgae = {}
    dgae = []
    for idx, row in enumerate(dgaer):
        metaphone = jellyfish.metaphone("%s %s %s" % (row['nombre'],
                                                      row['apellido1'],
                                                      row['apellido2']))
        # este diccionario permite unir el indice en DGAE con cuenta en SAEP
        idx_dgae[metaphone] = idx
        dgae.append(row)


    # DGAE repite renglones por estudiante, por cada grado academico
    # a continuacion generamos una lista y la guardamos en un diccionario
    # con el indice DGAE como llave
    campos_grado = ["antecedente_academico", "nivel_antecedente_academico", "promedio",
                    "estatus_graduacion", "fecha_graduacion", "entidad_academica",
                    "institucion", "pais_antecedente_academico",
                    "antecedente_academico_ingreso", "estado_antecedente_academico",
                    "completa", "completada_en_fecha"]

    grados_dgae = {}
    for row in dgae:
        grado = {}
        for c in campos_grado:
            grado[c] = row[c]

        metaphone = jellyfish.metaphone("%s %s %s" % (row['nombre'],
                                                      row['apellido1'],
                                                      row['apellido2']))

        if metaphone in grados_dgae:
            grados_dgae[metaphone].append(grado)
        else:
            grados_dgae[metaphone] = [grado, ]


    # por otro lado hacemos un diccionario de alumnos DGAE
    # cuya llave es el indice DGAE
    alumno_dgae = {}
    for idx, a in enumerate(dgae):
        # tirar todo lo que se repite
        for c in campos_grado + ['orientacion_interdisciplinaria',
                                 'estatus_orientacion_interdisciplinaria',
                                 'documentos_personales',
                                 'documentos_administrativos',
                                 'documentos_academicos']:
            a.pop(c)
            alumno_dgae[idx] = a


    # Cargar todos los alumnos nuevos a la base de datos
    print('-------------------------------- cargando nuevos ingresos ----------------------')
    for m in nuevos_saep:
        
        a = nuevos_saep[m] | alumno_dgae[idx_dgae[m]]
        a['grados'] = grados_dgae[m]

        print(a)
        
        u = get_user(a)

        p, created = models.Perfil.objects.get_or_create(user = u)

        p.curp = a['curp']
        p.telefono = str(a['telefono'])
        p.direccion1 = a['direccion']
        p.genero = a['genero']
        p.nacionalidad = a['nacionalidad']
        dia, mes, anyo = [int(n) for n in a['fecha_nacimiento'].split('/')]
        p.fecha_nacimiento = datetime(anyo, mes, dia)
        p.save()

        if created:
            print('nuevo perfil', p)
        else:
            print('update perfil', p)

        e, created = models.Estudiante.objects.get_or_create(user=u,
                                                             cuenta=a['cuenta'])
        e.save()

        if created:
            print('creado estudiante', e)
        else:
            print('update estudiante', e)

        # crear registro en historial
        year, semestre = a['semestre'].split('-')
        if a['nivel'] == 'M':
            plan = 'Maestría'
        elif a['nivel'] == 'D':
            plan = 'Doctorado'
        else:
            print('[NUEVOS][ERROR] plan no válido', a)


        h, created = models.Historial.objects.get_or_create(
            fecha = date.today(),
            estudiante = e,
            year = year,
            semestre = semestre,
            plan = plan,
            estado = 'inscrito',
        )

        h.institucion = get_institucion(int(a['entidad']))

        print('***%s***' % a['campo_conocimiento_seleccionado'])
        if plan == 'Maestría':
            h.campo_conocimiento = models.CampoConocimiento.objects.get(
                nombre__icontains=a['campo_conocimiento_seleccionado'])
        elif plan == 'Doctorado':
            h.lineas_investigacion = models.LineaInvestigacion.objects.get(
                nombre__icontains=a['campo_conocimiento_seleccionado'])
            
        h.save()
        
        e.estado = e.ultimo_estado()
        e.plan = e.ultimo_plan()
        e.save()
        
        # TODO: cargar grados, 
        

    # Cargar todos los reingresos a la base de datos
    print('-------------------------------- cargando reingresos ----------------------')
    for m in reingresos:

        a = reingresos[m]

        if models.Estudiante.objects.filter(cuenta=a['cuenta']).count() == 0:
            print("[REINGRESO][ERROR] fila", m, a, 'imposible reingresar estudiante sin registro previo')
            continue

        e = models.Estudiante.objects.get(cuenta=a['cuenta'])
        year, semestre = a['semestre'].split('-')
        if a['nivel'] == 'M':
            plan = 'Maestría'
        elif a['nivel'] == 'D':
            plan = 'Doctorado'
        else:
            print('[REINGRESO][ERROR] plan no válido', a)


        h, created = models.Historial.objects.get_or_create(
            fecha = date.today(),
            estudiante = e,
            year = year,
            semestre = semestre,
            plan = plan,
            estado = 'inscrito',
        )

        h.institucion = get_institucion(int(a['entidad']))
        h.save()
        
        e.estado = e.ultimo_estado()
        e.plan = e.ultimo_plan()
        e.save()

        print('historial actualizado', h)





def get_user(a):
    # usamos el lado izquierdo de su correo como username, o su cuenta
    username = a['correo'].split('@')[0]
    if models.User.objects.filter(username=username).count() > 0:
        # ya existe usuario con ese username!
        u = models.User.objects.get(username=username)
        if models.Estudiante.objects.filter(user=u,
                                            cuenta=a['cuenta']).count() == 0:
            # pero no hay estudiante con esa cuenta, de modo que es alguien más
            # para evitar colisión usar su cuenta como nombre de usuario
            username = a['cuenta']

    u, created = models.User.objects.get_or_create(
        username = username,
        email = a['correo']
    )

    if created:
        u.first_name = a['nombre']
        u.last_name = "%s %s" % (a['apellido1'], a['apellido2'])
        u.save()
        print('nuevo usuario', u, u.first_name, u.last_name)
    else:
        print('usuario encontrado', u)

    return u


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
