# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin.models import CampoConocimiento, LineaInvestigacion


class Command(BaseCommand):
    help = 'Carga entidades del PCS'

    def handle(self, *args, **options):
        load()


def load():
    campos = [
        "Contextos urbanos",
        "Manejo de sistemas acuáticos",
        "Política, gobernanza e instituciones",
        "Restauración ambiental",
        "Sistemas energéticos",
        "Vulnerabilidad y respuesta al cambio global",
    ]

    for c in campos:
        campo = CampoConocimiento(nombre=c)
        campo.save()

    lineas = [
        "Cambio global, vulnerabilidad y resiliencia",
        "Sistemas sociambientales, complejidad y adaptación",
        "Gobernanza, planeación colaborativa y aprendizaje social",
        "Límites, trayectorias y transición a la sostenibilidad",
        "Monitoreo y evaluación de sistemas socioambientales",
        "Urbanismo e infraestructura sostenible",
        "Diseño de sistemas sociotecnológicos", ]

    for l in lineas:
        linea = LineaInvestigacion(nombre=l)
        linea.save()
