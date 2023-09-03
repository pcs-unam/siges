# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from datetime import datetime, date
import argparse
import csv
from pprint import pprint
from pyexcel_ods3 import get_data
import jellyfish


class Command(BaseCommand):
    help = u'Importa base de datos de solicitantes aceptados'

    def add_arguments(self, parser):
        parser.add_argument('--solicitud',  # dgae
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo de solicitantes en formato csv')

        parser.add_argument('--status',  # saep
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo status en formato csv')

        parser.add_argument('--inscritos',
                            required=True,
                            type=argparse.FileType('r'),
                            help='path al archivo de inscritos en formato csv')



    def handle(self, *args, **options):

        importa(options['solicitud'], options['status'], options['inscritos'])




def importa(solicitud, status, inscritos):
    statr = csv.DictReader(status)
    solr = csv.DictReader(solicitud)
    inscritos = get_data(inscritos.name)

    k = list(inscritos.keys())[0]  # nombre de la primer hoja en el ODS

    ins = {}
    for i in range(0, len(inscritos[k])):
        a = inscritos[k][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: a.index(f)
                   for f in a}
            continue
        elif len(a) == 0:
            # descartar lineas vacias
            continue
        elif a[idx['cuenta']] == '':
            # descartar estudiantes sin correo
            print(f'[ERROR] fila {i} sin cuenta imposible importar')
            continue

        # diccionario de inscritos, correo por llave, row es valor
        institucion = get_institucion(int(a[idx['entidad_nombre']].split(' ')[0]))
        if '4172' in a[idx['plan_nombre']]:
            plan = 'Maestría'
        elif '5172' in a[idx['plan_nombre']]:
            plan = 'Doctorado'
        else:
            print(f'[ERROR] fila {i} plan no válido', a)
            plan = None


        es = {'cuenta': a[idx['cuenta']],
              'nombre_completo': a[idx['alumno_nombre']],
              'correo': a[idx['correo electronico']],
              'orienta': a[idx['orienta_nombre']],
              'plan': plan,
              'institucion': institucion,
              'tipo': a[idx['tipo']]}

        ins[a[idx['cuenta']]] = es

    aceptados = {}
    for row in statr:
        if row['aceptado'] == 'true':
            aceptados[row['folio']] = row


    # solicitud repite renglones por estudiante, por cada grado academico
    # a continuacion generamos una lista y la guardamos en un diccionario
    # con el indice DGAE como llave
    campos_grado = ["antecedente_academico", "nivel_antecedente_academico", "promedio",
                    "estatus_graduacion", "fecha_graduacion", "entidad_academica",
                    "institucion", "pais_antecedente_academico",
                    "antecedente_academico_ingreso", "estado_antecedente_academico",
                    "completa", "completada_en_fecha"]

    grados_sol = {}
    for row in solr:
        if row['folio'] not in aceptados:
            continue

        grado = {}
        for c in campos_grado:
            grado[c] = row[c]

        if row['folio'] in grados_sol:
            grados_sol[row['folio']].append(grado)
        else:
            grados_sol[row['folio']] = [grado, ]

        aceptados[row['folio']].update(row)
        aceptados[row['folio']]['grados'] = grados_sol[row['folio']]


    # aqui los tenemos, aceptados con los datos de la solicitud
    extra_correo = {}
    for folio in aceptados:
        a = aceptados[folio]
        extra_correo[a['correo']] = aceptados[folio]

    extra_cuenta = {}
    for folio in aceptados:
        a = aceptados[folio]
        if 'cuenta' in a:
            extra_cuenta[a['cuenta']] = aceptados[folio]

    extra_metaphone = {}
    for folio in aceptados:
        a = aceptados[folio]
    
        metaphone = jellyfish.metaphone("%s %s %s" % (a['apellido1'],
                                                      a['apellido2'],
                                                      a['nombre']))
        extra_metaphone[metaphone] = aceptados[folio]


    def get_extra(cuenta=None, correo=None, metaphone=None):
        if cuenta:
            return extra_cuenta.get(cuenta, {})
        elif correo:
            return extra_correo.get(correo, {})
        elif metaphone:
            return extra_metaphone.get(metaphone, {})
        else:
            return {}
        
        
    for a in ins:
        est = ins[a]

        extra = get_extra(cuenta=est['cuenta'])
        if extra == {}:
            extra = get_extra(correo=est['correo'])
        if extra == {}:            
            metaphone = jellyfish.metaphone(est['nombre_completo'])
            extra = get_extra(metaphone=metaphone)

        print(est, extra)


    # for a in aceptados:

    #     u = get_user(a)

    #     p, created = models.Perfil.objects.get_or_create(user=u)

    #     p.curp = a['curp']
    #     p.telefono = str(a['telefono'])
    #     p.direccion1 = a['direccion']
    #     p.genero = a['genero']
    #     p.nacionalidad = a['nacionalidad']
    #     dia, mes, anyo = [int(n) for n in a['fecha_nacimiento'].split('/')]
    #     p.fecha_nacimiento = datetime(anyo, mes, dia)
    #     p.save()

    #     if created:
    #         print('nuevo perfil', p)
    #     else:
    #         print('update perfil', p)

    #     e, created = models.Estudiante.objects.get_or_create(user=u,
    #                                                          cuenta=a['cuenta'])
    #     e.save()

    #     if created:
    #         print('creado estudiante', e)
    #     else:
    #         print('update estudiante', e)

    #     # crear registro en historial
    #     year, semestre = a['semestre'].split('-')
    #     if a['nivel'] == 'M':
    #         plan = 'Maestría'
    #     elif a['nivel'] == 'D':
    #         plan = 'Doctorado'
    #     else:
    #         print('[NUEVOS][ERROR] plan no válido', a)


    #     h, created = models.Historial.objects.get_or_create(
    #         fecha = date.today(),
    #         estudiante = e,
    #         year = year,
    #         semestre = semestre,
    #         plan = plan,
    #         estado = 'inscrito',
    #     )

    #     h.institucion = get_institucion(int(a['entidad']))

    #     if 'campo_conocimiento_seleccionado' in a:
    #         if plan == 'Maestría':
    #             h.campo_conocimiento = models.CampoConocimiento.objects.get(
    #                 nombre__icontains=a['campo_conocimiento_seleccionado'])
    #         elif plan == 'Doctorado':
    #             h.lineas_investigacion = models.LineaInvestigacion.objects.get(
    #                 nombre__icontains=a['campo_conocimiento_seleccionado'])
    #     else:
    #         print('[NUEVOS][WARN] sin campo de conocimiento')

    #     h.save()

    #     e.estado = e.ultimo_estado()
    #     e.plan = e.ultimo_plan()
    #     e.save()

    #     # cargar grados,
    #     for g in a['grados']:

    #         if g['nivel_antecedente_academico'] == 'L':
    #             nivel = 'licenciatura'
    #         elif g['nivel_antecedente_academico'] == 'M':
    #             nivel = 'maestria'
    #         elif g['nivel_antecedente_academico'] == 'D':
    #             nivel = 'doctorado'

    #         institucion = get_institucion_by_names(entidad=g['entidad_academica'],
    #                                                institucion=g['institucion'],
    #                                                estado=g['estado_antecedente_academico'],
    #                                                pais=g['pais_antecedente_academico'])


    #         if g['estatus_graduacion'] == 'Titulado o graduado':
    #             day, month, year = g['fecha_graduacion'].split('/')
    #             g, created = models.GradoAcademico.objects.get_or_create(
    #                 user=u,
    #                 nivel=nivel,
    #                 institucion=institucion,
    #                 grado_obtenido=g['antecedente_academico'],
    #                 fecha_obtencion=datetime(int(year), int(month), int(day)))

    #             print('grado academico', e, g)
    #             # TODO: 'promedio': '8.67',
    #             # TODO: en proceso o trunca

    # # Cargar todos los reingresos a la base de datos
    # print('-------------------------------- cargando reingresos ----------------------')
    # for m in reingresos:

    #     a = reingresos[m]

    #     if models.Estudiante.objects.filter(cuenta=a['cuenta']).count() == 0:
    #         print("[REINGRESO][ERROR] fila", m, a, 'imposible reingresar estudiante sin registro previo')
    #         continue

    #     e = models.Estudiante.objects.get(cuenta=a['cuenta'])
    #     year, semestre = a['semestre'].split('-')
    #     if a['nivel'] == 'M':
    #         plan = 'Maestría'
    #     elif a['nivel'] == 'D':
    #         plan = 'Doctorado'
    #     else:
    #         print('[REINGRESO][ERROR] plan no válido', a)


    #     h, created = models.Historial.objects.get_or_create(
    #         fecha = date.today(),
    #         estudiante = e,
    #         year = year,
    #         semestre = semestre,
    #         plan = plan,
    #         estado = 'inscrito',
    #     )

    #     h.institucion = get_institucion(int(a['entidad']))
    #     h.save()

    #     e.estado = e.ultimo_estado()
    #     e.plan = e.ultimo_plan()
    #     e.save()

    #     print('historial actualizado', h)





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

def get_institucion_by_names(entidad, institucion, estado, pais):
    if 'UNAM' in entidad:
        dependencia_UNAM = True
    else:
        dependencia_UNAM = False

    i, created = models.Institucion.objects.get_or_create(
        nombre=entidad,
        suborganizacion=institucion,
        dependencia_UNAM=dependencia_UNAM,
        estado=estado,
        pais=pais)
    if created:
        print("nueva institucion", i)
    return i
