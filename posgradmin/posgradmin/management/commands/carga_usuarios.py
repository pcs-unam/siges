# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from django.contrib.auth.models import User
import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import csv


class Command(BaseCommand):
    help = 'Carga usuarios desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'),
                            required=True,
                            help='archivo CSV con cursos')

    def handle(self, *args, **options):
        notas = load(options['csv'])

        if notas:
            orden = ['cuenta', 'email', 'paterno', 'materno', 'nombres']

            print ",".join(orden)
            for n in notas:
                print ",".join([n[k] for k in orden]), n['notas']


def load(f):
    reader = csv.DictReader(f, delimiter=",", quotechar='"')
    notas = []
    for row in reader:
        print row

        try:
            validate_email(row['email'].decode('utf8'))
            cuenta = row['cuenta']
            u = User(username=cuenta,
                     email=row['email'].decode('utf8'))
            u.first_name = row['nombres'].decode('utf8')
            u.last_name = u"%s %s" % (row['paterno'].decode('utf8'),
                                      row['materno'].decode('utf8'))
            u.password = u'pbkdf2_sha256$36000$wAcW7cBkfTcw$AmKBje123fdSHcvz/3PpchHJ+BEcOBe9km1exOvL+123'
            u.save()

        except ValidationError:
            cuenta = slugify.slugify(u"%s %s %s %s" % (
                row['cuenta'].decode('utf8'),
                row['nombres'].decode('utf8'),
                row['paterno'].decode('utf8'),
                row['materno'].decode('utf8')))

    return notas
