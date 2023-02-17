from django.core.management.base import BaseCommand
from posgradmin import models
from datetime import datetime, date, timedelta
import argparse


class Command(BaseCommand):
    
    help = """

Recorre fechas de registros segun el calendario escolar. Correr solo una vez!

per issue #272:
Recorrer en los semestres "1" un año al pasado
Recorrer en los semestres "2" seis meses al pasado
"""             

    def handle(self, *args, **options):

        recorre()




def recorre():
    for h in models.Historial.objects.all():
        if h.semestre == 1:
            antes = h.fecha - timedelta(days=365)
        elif h.semestre == 2:
            antes = h.fecha - timedelta(days=182)            
        h.fecha = antes
        h.save()

