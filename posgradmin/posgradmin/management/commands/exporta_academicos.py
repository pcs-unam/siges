# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin.models import Academico, LineaInvestigacion, CampoConocimiento
from django.template.loader import render_to_string
from os import path
from django.db.models import Q
from datetime import datetime
import random
from sh import mkdir
from django.utils.text import slugify

class Command(BaseCommand):
    help = u'Exporta académicos a formato markdown para la página'

    def add_arguments(self, parser):
        parser.add_argument('outdir',
                            help='path al directorio donde escribir')

    def handle(self, *args, **options):
        export(options['outdir'])


def export(outdir):
    last_year = datetime.now().year - 1
    doctorado = Academico.objects.filter(
        Q(acreditacion='D'),
        Q(fecha_acreditacion__year__gte=last_year)
        | Q(ultima_reacreditacion__year__gte=last_year)
    ).order_by('user__last_name')

    maestria = Academico.objects.filter(
        Q(acreditacion='M'),
        Q(fecha_acreditacion__year__gte=last_year)
        | Q(ultima_reacreditacion__year__gte=last_year)
    ).order_by('user__last_name')

    mkdir('-p', outdir)
    index_md = path.join(outdir, 'indice.md')

    # escribir el indice por nombre
    with open(index_md, 'w') as f:
        f.write(render_to_string('posgradmin/index_academicos.md',
                                 {'doctorado': doctorado,
                                  'maestria': maestria,
                                  'pleca': random.randint(0, 19)
                                  }).encode('utf-8'))


    # escribir el indice por linea de investigacion
    for linea in LineaInvestigacion.objects.all():

        academicos = linea.academico_set.filter(
            Q(acreditacion='D'),
            Q(fecha_acreditacion__year__gte=last_year)
            | Q(ultima_reacreditacion__year__gte=last_year)
        ).order_by('user__last_name')

        index_md = path.join(outdir, 'indice_%s.md' % slugify(linea.nombre))
        with open(index_md, 'w') as f:
            f.write(render_to_string('posgradmin/index_academicos_linea.md',
                                     {'academicos': academicos,
                                      'linea': linea,
                                      'link': slugify(linea.nombre),
                                      'pleca': random.randint(0, 19)
                                     }).encode('utf-8'))


    # escribir el indice por campo de conocimiento
    for campo in CampoConocimiento.objects.all():

        academicos = campo.academico_set.filter(
            Q(acreditacion='M') | Q(acreditacion='D'),
            Q(fecha_acreditacion__year__gte=last_year)
            | Q(ultima_reacreditacion__year__gte=last_year)
        ).order_by('user__last_name')

        index_md = path.join(outdir, 'indice_%s.md' % slugify(campo.nombre))
        with open(index_md, 'w') as f:
            f.write(render_to_string('posgradmin/index_academicos_campo.md',
                                     {'academicos': academicos,
                                      'campo': campo,
                                      'link': slugify(campo.nombre),
                                      'pleca': random.randint(0, 19)
                                     }).encode('utf-8'))


    # palabras = {}
    # for a in Academico.objects.all():
    #     for p in a.palabras_clave.split(','):
    #         if "\r\n" in p:
    #             for pp in p.split("\r\n"):
    #                 pc = pp.strip().lower()
    #                 if pc in palabras:
    #                     palabras[pc].add(a)
    #                 else:
    #                     palabras[pc] = set([a, ])
    #         else:
    #             pc = p.strip().lower()
    #             if pc in palabras:
    #                 palabras[pc].add(a)
    #             else:
    #                 palabras[pc] = set([a, ])
    # from pprint import pprint
    # pprint(palabras)

    # escribir los perfiles
    mkdir('-p', path.join(outdir, 'perfiles'))
    academicos = [a for a in doctorado] + [a for a in maestria]
    for a in academicos:
        a_md = path.join(outdir,
                         'perfiles',
                         '%s.md' % a.user.username)

        palabras_clave = a.palabras_clave.split("\n")

        with open(a_md, 'w') as f:
            f.write(render_to_string(
                'posgradmin/academico.md',
                {'a': a,
                 'palabras_clave': palabras_clave,
                 'pleca': random.randint(0, 19)
                 }).encode('utf8'))
