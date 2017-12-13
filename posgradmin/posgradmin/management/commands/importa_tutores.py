# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from posgradmin.models import Academico, Institucion, Perfil, Empleo, \
    Solicitud
from django.contrib.auth.models import User
import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import csv


class Command(BaseCommand):
    help = 'Importa académicos desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV con cursos')
        parser.add_argument('--admin',
                            required=True,
                            help='username de admin cargando datos')

    def handle(self, *args, **options):
        notas = load(options['csv'], options['admin'])

        if notas:
            orden = ['Grado', 'Apellido Paterno', 'Apellido Materno',
                     'Nombres', 'suborganizacion', 'Institucion',
                     'Líneas de investigación', 'correo electrónico',
                     'RFC', 'CURP', 'SNI', 'PRIDE', 'CVU',
                     'NOMBRAMIENTO', 'Tipo']

            print ",".join(orden)
            for n in notas:
                print ",".join([n[k] for k in orden]), n['notas']


def load(f, admin):
    admin = User.objects.get(username=admin)

    reader = csv.DictReader(f, delimiter="|", quotechar='"')
    notas = []
    for row in reader:
        print row
        # cargar o leer la Institución
        if "Universidad Nacional Autónoma de México" in row['Institucion'] \
           or "UNAM" in row['Institucion']:
            dependencia_unam = True
        else:
            dependencia_unam = False

        if row["Institucion"] == "":
            row["Institucion"] = row["suborganizacion"]
        institucion, creada = Institucion.objects.get_or_create(
            nombre=row["Institucion"],
            suborganizacion=row["suborganizacion"],
            dependencia_unam=dependencia_unam)
        if creada:
            row['notas'] = ["Institución nueva, cargada", ]

        try:
            validate_email(row['correo electrónico'].decode('utf8'))
            cuenta = slugify.slugify(
                row['correo electrónico'].split('@')[0].decode('utf8'))
            if User.objects.filter(username=cuenta).count() > 0:
                cuenta = slugify.slugify(u"%s %s %s" % (
                    row['Nombres'].decode('utf8'),
                    row['Apellido Paterno'].decode('utf8'),
                    row['Apellido Materno'].decode('utf8')))
        except ValidationError:
            cuenta = slugify.slugify(u"%s %s %s" % (
                row['Nombres'].decode('utf8'),
                row['Apellido Paterno'].decode('utf8'),
                row['Apellido Materno'].decode('utf8')))

#        try:
        u = User(username=cuenta,
                 email=row['correo electrónico'].decode('utf8'))
        u.first_name = row['Nombres'].decode('utf8')
        u.last_name = u"%s %s" % (row['Apellido Paterno'].decode('utf8'),
                                  row['Apellido Materno'].decode('utf8'))
        u.password = u'pbkdf2_sha256$36000$wAcW7cBkfTcw$AmKBje123fdSHcvz/3PpchHJ+BEcOBe9km1exOvL+123'
        u.save()

        p = Perfil(
            user=u,
            curp=row['CURP'],
            rfc=row['RFC'])
        p.save()

        s = Solicitud(
            resumen=u"importar académico %s" % u,
            tipo="otro",
            solicitante=admin,
            descripcion="Solicitud creada automáticamente"
            + "para la carga de datos",
            estado="atendida")
        s.save()

        a = Academico(
            user=u,
            titulo=row['Grado'],
            nivel_pride=row['PRIDE'],
            nivel_SNI=row['SNI'],
            CVU=row['CVU'],
            tutor=True,
            comite_academico=False,
            acreditacion=row['Tipo'],
            lineas=row['Líneas de investigación'],
            solicitud=s)
        a.save()

        empleo = Empleo(
            user=u,
            institucion=institucion,
            cargo=row['NOMBRAMIENTO'])
        empleo.save()

    return notas
