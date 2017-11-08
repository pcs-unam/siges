# coding: utf8

from django.core.management.base import BaseCommand
from posgradmin import etl
import argparse


class Command(BaseCommand):
    help = 'Cargar alumnos desde un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=argparse.FileType('r'), required=True,
                            help='archivo CSV con alumnos.')

        parser.add_argument('--ingreso', type=int, required=True,
                            help='año de ingreso')

        parser.add_argument('--semestre', type=int, required=True,
                            help='semestre de ingreso (1 o 2)')

    def handle(self, *args, **options):
        etl.load(options['csv'],
                 options['ingreso'],
                 options['semestre'])
