# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from django.core import serializers
import pickle


class Command(BaseCommand):
    help = u'Fija algunos objetos en archivos json para restaurarlos tras migracion, leer queries en el codigo.'

    def handle(self, *args, **options):
        fix_some()



def fix_some():

    # fijar usuarios con estudiante
    users = [u for u in models.User.objects.all()
            if hasattr( u, 'estudiante')]

    estudiantes = {e.user.username:e for e in models.Estudiante.objects.all()}
    academicos = {}
    acreditaciones = {}
    
    # que no sean estudiantes ni académicos
    users += [u for u in models.User.objects.all()
             if not hasattr( u, 'academico')
             and not hasattr(u, 'estudiante')]

    for uid in [390,
                476,
                719,
                720,
                721,
                723,
                840,]:
        u = models.User.objects.get(pk=uid)
        users.append(u)
        if hasattr(u, 'estudiante'):
            estudiantes[u.username] = u.estudiante

        if hasattr(u, 'academico'):
            academicos[u.username] = u.academico
            acreditaciones[u.username] = []
            for ac in u.academico.acreditaciones.all():
                acreditaciones[u.username].append(ac)

    grados = {}
    for u in users:
        for a in u.gradoacademico_set.all():
            if u.username in grados:
                grados[u.username].append(a)
            else:
                grados[u.username] = [a, ]

    perfiles = {u.username: u.perfil for u in users
                if hasattr(u, 'perfil')}

    adscripciones = {}
    for username in perfiles:
        p = perfiles[username]
        for a in p.adscripcion_set.all():
            if username in adscripciones:
                adscripciones[username].append(a)
            else:
                adscripciones[username] = [a, ]



    with open("../import_2023/undelete_users.json", "w") as out:
        serializers.serialize("json", users, stream=out)

    with open("../import_2023/undelete_estudiantes.pickle", "wb") as out:
        pickle.dump(estudiantes, out)

    with open("../import_2023/undelete_academicos.pickle", "wb") as out:
        pickle.dump(academicos, out)

    with open("../import_2023/undelete_acreditaciones.pickle", "wb") as out:
        pickle.dump(acreditaciones, out)
        
    with open("../import_2023/undelete_perfiles.pickle", "wb") as out:
        pickle.dump(perfiles, out)

    with open("../import_2023/undelete_grados.pickle", "wb") as out:
        pickle.dump(grados, out)

    with open("../import_2023/undelete_adscripciones.pickle", "wb") as out:
        pickle.dump(adscripciones, out)
