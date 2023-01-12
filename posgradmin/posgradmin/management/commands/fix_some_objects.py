# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from django.core import serializers



class Command(BaseCommand):
    help = u'Fija algunos objetos en archivos json para restaurarlos tras migracion, leer queries en el codigo.'

    def handle(self, *args, **options):
        fix_some()



def fix_some():

    # fijar usuarios con estudiante
    data = [u for u in models.User.objects.all()
            if hasattr( u, 'estudiante')]

    # que no sean estudiantes ni académicos
    data += [u for u in models.User.objects.all()
             if not hasattr( u, 'academico')
             and not hasattr(u, 'estudiante')]
    
    with open("../import_2023/undelete_me.json", "w") as out:
        serializers.serialize("json", data, stream=out)
    




