# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from django.contrib.auth.models import User
from posgradmin.models import Academico
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
        # titulo,apellidos,nombres,lineas,email,sni,pride,cvu,tutor,acreditacion,

        validate_email(row['email'].strip().decode('utf8'))
        cuenta = row['email'].split('@')[0]
        u = User(username=cuenta.lower(),
                 email=row['email'].decode('utf8'))
        u.first_name = row['nombres'].decode('utf8')
        u.last_name = row['apellidos']
        u.password = u'pbkdf2_sha256$36000$wAcW7cBkfTcw$AmKBje123fdSHcvz/3PpchHJ+BEcOBe9km1exOvL+123'

        u.save()

        if not row['pride'].strip():
            nivel_PRIDE = 'sin PRIDE'
        else:
            nivel_PRIDE = row['pride'].decode('utf8')

        if not row['sni'].strip():
            nivel_sni = 'sin SNI'
        else:
            if row['sni'].decode('utf8') == '1':
                nivel_sni = 'I'
            elif row['sni'].decode('utf8') == '2':
                nivel_sni = 'II'
            elif row['sni'].decode('utf8') == '3':
                nivel_sni = 'III'
            elif row['sni'].decode('utf8') == '2':
                nivel_sni = row['sni'].decode('utf8')

        a = Academico(user=u,
                      titulo=row['titulo'].decode('utf8'),
                      nivel_PRIDE=nivel_PRIDE,
                      nivel_SNI=nivel_sni,
                      CVU=row['cvu'].decode('utf8'),
                      lineas=row['lineas'].decode('utf8'),
                      acreditacion=row['acreditacion'].decode('utf8'))
        a.save()
