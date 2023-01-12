# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin import models
from os import path
from django.core import serializers


class Command(BaseCommand):
    help = u'Carga algunos objetos en archivos json a la base de datos. Ver fix_some_objects.'

    def handle(self, *args, **options):
        undelete_some()



def undelete_some():

    for u in serializers.deserialize('json',
                                     open("../import_2023/undelete_me.json").read()):
            
        if models.User.objects.filter(username=u.object.username).count() == 0:
            print('undeleting', u.object.username)
            u.save()

    
