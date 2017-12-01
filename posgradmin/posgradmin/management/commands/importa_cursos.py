# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from posgradmin.models import Curso

import csv


class Command(BaseCommand):
    help = 'Importa cursos desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV con cursos')

    def handle(self, *args, **options):
        notas = load(options['csv'])

        if notas:
            orden = ["Curso", "Clave", "Creditos",
                     "Horas por semestre", "Tipo"]
            print ",".join(orden)
            for n in notas:
                print ",".join([n[k] for k in orden])


def load(f):
    reader = csv.DictReader(f, delimiter="\t")
    notas = []
    for row in reader:
        print row
        c = Curso(asignatura=row['Curso'].decode('utf8'),
                  clave=row['Clave'],
                  creditos=row['Creditos'],
                  horas_semestre=row['Horas por semestre'],
                  tipo=row['Tipo'].decode('utf8'))
        print c.tipo
        c.save()
    return notas
