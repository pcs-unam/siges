# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin.models import Institucion


class Command(BaseCommand):
    help = 'Carga entidades del PCS'

    def handle(self, *args, **options):
        load()


def load():
    entidades = [
        "Facultad de Arquitectura",
        "Facultad de Ciencias",
        "Escuela Nacional de Estudios Superiores Unidad León",
        "Escuela Nacional de Estudios Superiores Unidad Morelia",
        "Instituto de Ecología",
        "Instituto de Ciencias del Mar y Limnología",
        "Instituto de Biología",
        "Instituto de Investigaciones Económicas",
        "Instituto de Investigaciones Sociales",
        "Instituto de Investigaciones en Ecosistemas y Sustentabilidad",
        "Instituto de Ingeniería",
        "Instituto de Energías Renovables", ]

    for e in entidades:
        i = Institucion(nombre="Universidad Nacional Autónoma de México",
                        suborganizacion=e,
                        pais="México",
                        dependencia_UNAM=True,
                        entidad_PCS=True)
        i.save()
