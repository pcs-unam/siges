# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from posgradmin.models import Estudiante, Entidad, Proyecto, \
    CampoConocimiento, Perfil, Institucion, Trabajo
from django.contrib.auth.models import User
import csv
from pprint import pprint


class Command(BaseCommand):
    help = 'Importa estudiantes desde un archivo CSV derivado de Genovevota'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV con estudiantes')

    def handle(self, *args, **options):
        notas = load(options['csv'])

        if notas:
            pprint(notas)
            # orden = ["cuenta", "nombre", "apellidos",
            #          "correo", "plan", "proyecto", "campo",
            #          "entidad", "error"]
            # print ",".join(orden)
            # for n in notas:
            #     print ",".join([n[k] for k in orden])


def load(f):
    reader = csv.DictReader(f, delimiter='|')

# 'Dependencia UNAM',
# 'Lugar Trabajo',
# 'Cargo',

    notas = {}
    for row in reader:
        notas[row['cuenta']] = [row, ]
        try:

            u = User(username=str(row['cuenta']))
            # Aguas: comentado asi para desarrollo
            u.email = row['email'] + ".example.com"
            u.first_name = row['nombre']
            apellidos = " ".join([row['apellido paterno'],
                                  row['apellido materno']])
            u.last_name = apellidos
            u.password = u'pbkdf2_sha256$36000$wAcW7cBkfTcw$AmKBje123fdSHcvz/3PpchHJ+BEcOBe9km1exOvL+123'
            u.save()
        except:
            notas[row['cuenta']].append('imposible crear usuario')
            continue

        entidad, creada = Entidad.objects.get_or_create(nombre=row["entidad"])
        entidad.domicilio = row['Entidad Domicilio']
        if creada:
            notas[row['cuenta']].append('Entidad creada')

        e = Estudiante(cuenta=row['cuenta'],
                       plan=row['plan'],
                       entidad=entidad,
                       ingreso=row['Generacion'],
                       semestre=1,
                       user=u)
        e.save()

        campo, creado = CampoConocimiento.objects.get_or_create(
            nombre=row["campo"])
        if creado:
            notas[row['cuenta']].append('Campo de Conocimiento creado')

        proyecto = Proyecto(nombre=row['proyecto'],
                            campo_conocimiento=campo,
                            estudiante=e,
                            aprobado=True)
        proyecto.save()

        p = Perfil(
            user=u,
            curp=row['CURP'],
            rfc=row['RFC'],
            telefono=row['Teléfono'],
            genero=row['Sexo'],
            nacionalidad=row['País'],
            fecha_nacimiento=row['Fecha Nacimiento'],

            estado_civil=row['Estado Civíl'],
            pasaporte=row['Pasaporte'])
        p.save()

        if row["Trabaja UNAM"] == "Si":
            dependencia_unam = True
            nombre = "UNAM"
            suborganizacion = "%s, %s" % (row["Dependencia UNAM"],
                                          row["Lugar Trabajo"])
        else:
            dependencia_unam = False
            nombre = row["Lugar Trabajo"]
            suborganizacion = ""

        if row["Lugar Trabajo"] != "":
            institucion, creada = Institucion.objects.get_or_create(
                nombre=nombre,
                suborganizacion=suborganizacion,
                dependencia_unam=dependencia_unam)
        if creada:
            notas[row['cuenta']].append("Institución nueva")

        trabajo = Trabajo(
            institucion=institucion,
            estudiante=e,
            cargo=row["Cargo"])
        trabajo.save()

    return notas
