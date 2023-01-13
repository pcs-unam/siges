# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from django.core import serializers
import jellyfish
import pickle

class Command(BaseCommand):
    help = u'Carga algunos objetos en archivos json a la base de datos. Ver fix_some_objects.'

    def handle(self, *args, **options):
        undelete_some()


def search_similar_names(u):
    u_name = u.get_full_name()
    if not u_name:
        return

    similar = []
    for user in models.User.objects.all():
        name = user.get_full_name()

        d = jellyfish.levenshtein_distance(u_name, name)
        if d <= 2 and u.id != user.id:
            similar.append(user)

    return similar


        
def undelete_users():
    for f in serializers.deserialize('json',
                                     open(f"../import_2023/undelete_users.json").read()):
        u = f.object
            
        if models.User.objects.filter(username=u.username).count() == 0:
            u.save()
            print(f'undeleted user {u}', u.id)
            dupes = search_similar_names(u)
            if dupes:
                print(u, dupes)
            print('\n')
    

def undelete_grados():
    with open('../import_2023/undelete_grados.pickle', 'rb') as f:
        grados = pickle.load(f)
        for username in grados:
            for g in grados[username]:
            
                if models.User.objects.filter(username=username).count() == 1:
                    u_db = models.User.objects.get(username=username)
                    g.user = u_db
                    g.save()
                    print(f'undeleted grado {u_db} {g}')
    

def undelete_academicos():
    with open('../import_2023/undelete_academicos.pickle', 'rb') as f:
        academicos = pickle.load(f)
    for username in academicos:
        a = academicos[username]
            
        if models.User.objects.filter(username=username).count() == 1:
            u_db = models.User.objects.get(username=username)
            a.user = u_db
            a.save()
            print(f'undeleted academico {u_db} {a}')

            
def undelete_acreditaciones():
    with open('../import_2023/undelete_acreditaciones.pickle', 'rb') as f:
        acreditaciones = pickle.load(f)
    for username in acreditaciones:
        if models.User.objects.filter(username=username).count() == 1:
            u_db = models.User.objects.get(username=username)
            academico = u_db.academico
        
            for a in acreditaciones[username]:
                a.academico = academico
                a.save()
                print(f'undeleted acreditacion {academico} {a}')


def undelete_adscripciones():
    with open('../import_2023/undelete_adscripciones.pickle', 'rb') as f:
        ads = pickle.load(f)
    for username in ads:
        if models.User.objects.filter(username=username).count() == 1:
            u_db = models.User.objects.get(username=username)
            for a in ads[username]:
                a.user = u_db
                a.save()
                print(f'undeleted adscripcion {u_db} {a}')


def undelete_some():

    undelete_users()
    undelete_grados()
    undelete_academicos()
    undelete_acreditaciones()
#    undelete_adscripciones()
