# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from posgradmin.models import Estudiante, Proyecto, CampoConocimiento
import csv


class Command(BaseCommand):
    help = """Carga año de ingreso, plan y entidad de estudiantes, desde CSV"""

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV')

    def handle(self, *args, **options):
        load(options['csv'])


def load(f):
    reader = csv.DictReader(f, delimiter=",", quotechar='"')
    for row in reader:
        print row  # cuenta,linea,proyecto

        campo, creado = CampoConocimiento.objects.get_or_create(
            nombre=row["linea"])
        if creado:
            print 'Campo de Conocimiento creado'

        e = Estudiante.objects.get(cuenta=row['cuenta'])

        p = Proyecto(nombre=row['proyecto'],
                     campo_conocimiento=campo,
                     estudiante=e,
                     aprobado=True)
        p.save()
