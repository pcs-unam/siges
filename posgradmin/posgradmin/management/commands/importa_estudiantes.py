# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from posgradmin.models import Estudiante, Entidad, Proyecto, \
    CampoConocimiento, Perfil
from django.contrib.auth.models import User
import csv


class Command(BaseCommand):
    help = 'Importa estudiantes desde un archivo CSV derivado de Genovevota'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV con estudiantes')

    def handle(self, *args, **options):
        notas = load(options['csv'])

        if notas:
            orden = ["cuenta", "nombre", "apellidos",
                     "correo", "plan", "proyecto", "campo",
                     "entidad", "error"]
            print ",".join(orden)
            for n in notas:
                print ",".join([n[k] for k in orden])


def load(f):
    reader = csv.DictReader(f)

# 'Dependencia UNAM',
# 'Lugar Trabajo',
# 'Cargo',

    notas = []
    for row in reader:
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
            row['notas_usuario'] = 'Imposible crear usuario'
            notas.append(row)
            break

        entidad, creada = Entidad.objects.get_or_create(nombre=row["entidad"])
        entidad.domicilio = row['Entidad Domicilio']
        if creada:
            row['notas_entidad'] = 'Entidad creada, posible error de captura'
            notas.append(row)

        e = Estudiante(cuenta=row['cuenta'],
                       plan=row['plan'],
                       entidad=entidad,
                       ingreso=row[u'Generación'],
#                       semestre=semestre,
                       user=u)
        e.save()

        campo, creado = CampoConocimiento.objects.get_or_create(
            nombre=row["campo"])
        if creado:
            row['notas_campo'] = 'Campo de Conocimiento creado'
            notas.append(row)

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

    return notas
