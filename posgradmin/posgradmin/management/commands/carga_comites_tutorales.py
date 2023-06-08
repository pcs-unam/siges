# coding: utf-8
from django.core.management.base import BaseCommand
import argparse
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from posgradmin import models
from django.core.validators import validate_email
from pyexcel_ods3 import get_data
import jellyfish


acads = {jellyfish.metaphone(a.nombre_completo()): a
         for a in models.Academico.objects.all()}

class Command(BaseCommand):
    help = 'Carga usuarios desde un archivo ods'

    def add_arguments(self, parser):
        parser.add_argument('--ods', type=argparse.FileType('r'),
                            required=True,
                            help='archivo ods con cursos')

    def handle(self, *args, **options):
        load(options['ods'])


def busca_acad(email):

    email = email.strip().replace(' ', '')
    if ',' in email:
        sep = ','
    elif ';' in email:
        sep = ';'
    elif '/' in email:
        sep = '/'
    else:
        sep = False

    if sep:
        for e in email.split(sep):
            if models.User.objects.filter(email=e).count() > 0:
                u = models.User.objects.get(email=e)
            elif EmailAddress.objects.filter(email=e).count() > 0:
                u = EmailAddress.objects.filter(email=e).first().user
            else:
                u = None
            if hasattr(u, 'academico'):
                return u.academico
    
    if models.User.objects.filter(email=email).count() > 0:
        u = models.User.objects.get(email=email)
    elif EmailAddress.objects.filter(email=email).count() > 0:
        u = EmailAddress.objects.filter(email=email).first().user
    else:
        u = None

    if hasattr(u, 'academico'):
        return u.academico

    return None


def busca_acad_name(name):
    metaphone = jellyfish.metaphone(name)
    return acads.get(metaphone, None)



def get_tipo(text):

    tipo_m = {
        'Tutor(a) principal de Doctorado (TPD)': 'TPD',
        'Cotutor(a) de Doctorado (CD)': 'CD',
        'Miembro de comité de Doctorado (MCD)': 'MCD',
        'Asesor Externo Doctorado (AED)': 'AED',
        'Tutor(a) principal de Maestría (TPM)': 'TPM',
        'Cotutor(a) de Maestría (CM)': 'CM',
        'Miembro de comité de Maestría (MCM)': 'MCM',
        'Asesor externo maestría (AEM)': 'AEM',
    }

    if text in tipo_m:
        return tipo_m[text]
    else:
        for v in tipo_m.values():
            if v in text:
                return v

    return None
            

        
def load(f):
    
    models.MembresiaComite.objects.all().delete()
    models.InvitadoMembresiaComite.objects.all().delete()
    
    data = get_data(f.name)    

    for i in range(0, len(data['CT'])):
        row = data['CT'][i]

        # generar indice de columnas usando el encabezado
        if i == 0:
            idx = {f: row.index(f)
                   for f in row}
            continue
        elif len(row) == 0:
            # descartar lineas vacias
            continue

        cuenta = row[idx['Cuenta']]
        if models.Estudiante.objects.filter(cuenta=cuenta).count() == 1:
            # estudiante existe!
            e = models.Estudiante.objects.get(cuenta=cuenta)
            year = row[idx['Año']]
            semestre = row[idx['Semestre']]
            tipo = get_tipo(row[idx['Tipo']])
        else:
            print(f'fila {i}: estudiante no encontrado: {cuenta}')
            continue


        if tipo == 'AEM' or tipo == 'AED':
            if len(row) < 5:
                print(f"fila {i}: data incompleta: {row}")
                continue
            print('externo', row)
        else:
            if len(row) < 6:
                print(f"fila {i}: data incompleta: {row}")
                continue

            email = row[idx['Correo tutor']]
                
            a = busca_acad(email)
            if not a:
                name = row[idx['Nombre tutor']]
                a = busca_acad_name(name)
                if not a:
                    print(f"fila {i}: académico no encontrado: {name} <{email}>")
                    continue
            
        # validate_email(row['miembro1'].strip().decode('utf8'))
        # u = User.objects.get(email=row['miembro1'].strip().decode('utf8'))
        # m1 = u.academico
        # m1.tutor = True
        # m1.save()


        # c = Comite(estudiante=e,
        #            miembro1=m1,
        #            miembro2=m2,
        #            miembro3=m3,
        #            tipo="tutoral")
        # c.save()

