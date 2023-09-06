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

        # diccionario de inscritos, cuenta por llave, row es valor
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
    extra_cuenta = {}
    extra_metaphone = {}   
    for folio in aceptados:
        a = aceptados[folio]
        
        extra_correo[a['correo']] = a

        if 'cuenta' in a:
            extra_cuenta[a['cuenta']] = a

        metaphone = jellyfish.metaphone("%s %s %s" % (a['apellido1'],
                                                      a['apellido2'],
                                                      a['nombre']))
        extra_metaphone[metaphone] = a


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

        print(est['tipo']) 
        e = get_estudiante(est, extra)
        u = e.user
        
        if extra != {}:
            p, p_created = models.Perfil.objects.get_or_create(user=u)
            p.curp = extra['curp']
            p.telefono = f"({extra['pais_telefono']}) extra['telefono']"
            p.telefono_movil = f"({extra['pais_celular']}) extra['celular']"
            p.direccion1 = extra.get('direccion', '')
            p.genero = extra['genero']
            p.nacionalidad = extra['nacionalidad']
            anyo, mes, dia = [int(n) for n in extra['fecha_nacimiento'].split('-')]
            p.fecha_nacimiento = datetime(anyo, mes, dia)
            p.save()
            
            if p_created:
                print('nuevo perfil', p)
            else:
                print('update perfil', p)
                

        # crear registro en historial
        #year, semestre = a['semestre'].split('-')
        now = datetime.now()
        year = now.year + 1
        if now.month > 6:
            semestre = 1
        else:
            semestre = 2
        
        h, h_created = models.Historial.objects.get_or_create(
            fecha = date.today(),
            estudiante = e,
            year = year,
            semestre = semestre,
            plan = est['plan'],
            estado = 'inscrito',
            institucion = est['institucion']
        )

        e.estado = e.ultimo_estado()
        e.plan = e.ultimo_plan()
        e.save()

        if 'grados' in extra:
            # cargar grados
            for g in extra['grados']:
                
                if g['nivel_antecedente_academico'] == 'L':
                    nivel = 'licenciatura'
                elif g['nivel_antecedente_academico'] == 'M':
                    nivel = 'maestria'
                elif g['nivel_antecedente_academico'] == 'D':
                    nivel = 'doctorado'

                institucion = get_institucion_by_names(entidad=g['entidad_academica'],
                                                       institucion=g['institucion'],
                                                       estado=g['estado_antecedente_academico'],
                                                       pais=g['pais_antecedente_academico'])

            

                if g['estatus_graduacion'] == 'Titulado o graduado':
                    year, month, day = g['fecha_graduacion'].split('-')
                    g, created = models.GradoAcademico.objects.get_or_create(
                        user=u,
                        nivel=nivel,
                        institucion=institucion,
                        grado_obtenido=g['antecedente_academico'],
                        fecha_obtencion=datetime(int(year), int(month), int(day)))

                    print(f'grado academico e<{e}> g<{g}>')
    #             # TODO: 'promedio': '8.67',
    #             # TODO: en proceso o trunca






def get_estudiante(a, extra):

    if models.Estudiante.objects.filter(cuenta=a['cuenta']).count() > 0:
        # estudiante ya existe
        e = models.Estudiante.objects.get(cuenta=a['cuenta'])
        
        # revisar aqui que sea reingreso
        if a['tipo'] == 'Reingreso':
            print(f"Reingreso de estudiante encontrado por cuenta {e}")
        else:
            print(f"[alerta] {a['tipo']} con estudiante ya existente {e}")

        if 'campo_conocimiento' in extra:
            if a['plan'] == 'Maestría':
                e.campo_conocimiento = models.CampoConocimiento.objects.get(
                    nombre__icontains=extra['campo_conocimiento'])
            elif a['plan'] == 'Doctorado':
                e.lineas_investigacion = models.LineaInvestigacion.objects.get(
                    nombre__icontains=extra['campo_conocimiento'])
            
        e.save()
        
    else:
        # nuevo estudiante
        if a['tipo'] != 'Primer ingreso':
            print(f"[alerta] {a['tipo']} pero no existe estudiante {a['cuenta']}")
            
        username = a['correo'].split('@')[0]
        if models.User.objects.filter(username=username).count() > 0:
            # username ya en uso, usemos cuenta como username
            if models.User.objects.filter(username=a['cuenta']).count() > 0:
                # ya hay usuario con cuenta por username
                print(f"ya existe {a['cuenta']} pero no hay estudiante con esa cuenta")
                u = models.User.objects.get(username=a['cuenta'])
            else:
                u = models.User(
                    username = a['cuenta'],
                    email = a['correo']
                )
        else:
            u = models.User(
                username = username,
                email = a['correo']
            )

        if extra != {}:
            u.first_name = extra['nombre']
            u.last_name = "%s %s" % (extra['apellido1'], extra['apellido2'])
            
        u.save()
        print(f'nuevo usuario {u.username}')

        
        e = models.Estudiante(user=u,
                              cuenta=a['cuenta'])

        if 'campo_conocimiento' in extra:
            if a['plan'] == 'Maestría':
                e.campo_conocimiento = models.CampoConocimiento.objects.get(
                    nombre__icontains=extra['campo_conocimiento'])
            elif a['plan'] == 'Doctorado':
                e.lineas_investigacion = models.LineaInvestigacion.objects.get(
                    nombre__icontains=extra['campo_conocimiento'])
        else:
            print('[alerta] nuevo ingreso sin campo o linea')
        
        e.save()

        print(f'nuevo estudiante {e}')
        
    return e
        

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
