# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from django.contrib.auth.models import User
from posgradmin.models import Estudiante
import csv


class Command(BaseCommand):
    help = """Carga año de ingreso, plan de estudiantes, desde CSV"""

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV')

    def handle(self, *args, **options):
        load(options['csv'])


def load(f):
    reader = csv.DictReader(f, delimiter=",", quotechar='"')
    for row in reader:
        print row

        u = User.objects.get(username=row['cuenta'])

        e = Estudiante(cuenta=row['cuenta'],
                       user=u,
                       ingreso=int(row['ingreso']),
                       plan=row['plan'].lower(),
                       semestre=1)

        e.save()
