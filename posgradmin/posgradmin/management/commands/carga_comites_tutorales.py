# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from django.contrib.auth.models import User
from posgradmin.models import Estudiante, Comite
from django.core.validators import validate_email

import csv


class Command(BaseCommand):
    help = 'Carga usuarios desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV con cursos')

    def handle(self, *args, **options):
        load(options['csv'])


def load(f):
    reader = csv.DictReader(f, delimiter=",", quotechar='"')
    for row in reader:
        print row
        # cuenta,miembro1,miembro2,miembro3

        validate_email(row['miembro1'].strip().decode('utf8'))
        u = User.objects.get(email=row['miembro1'].strip().decode('utf8'))
        m1 = u.academico
        m1.tutor = True
        m1.save()

        if not row['miembro2']:
            m2 = None
        else:
            validate_email(row['miembro2'].strip().decode('utf8'))
            u = User.objects.get(email=row['miembro2'].strip().decode('utf8'))
            m2 = u.academico
            m2.tutor = True
            m2.save()
        if not row['miembro3']:
            m3 = None
        else:
            validate_email(row['miembro3'].strip().decode('utf8'))
            u = User.objects.get(email=row['miembro3'].strip().decode('utf8'))
            m3 = u.academico
            m3.tutor = True
            m3.save()
        e = Estudiante.objects.get(cuenta=row['cuenta'])

        c = Comite(estudiante=e,
                   miembro1=m1,
                   miembro2=m2,
                   miembro3=m3,
                   tipo="tutoral")
        c.save()
