# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin.models import Academico
from django.template.loader import render_to_string
from os import path
from django.db.models import Q
from datetime import datetime


class Command(BaseCommand):
    help = 'Exporta académicos a formato markdown para la página'

    def add_arguments(self, parser):
        parser.add_argument('outdir',
                            help='path al directorio donde escribir')

    def handle(self, *args, **options):
        export(options['outdir'])


def export(outdir):
    last_year = datetime.now().year - 1
    doctorado = Academico.objects.filter(
        Q(acreditacion='D'),
        Q(disponible_tutor=True) | Q(disponible_miembro=True),
        Q(fecha_acreditacion__year__gte=last_year)
        | Q(ultima_reacreditacion__year__gte=last_year)
    ).order_by('user__last_name')

    maestria = Academico.objects.filter(
        Q(acreditacion='M'),
        Q(disponible_tutor=True) | Q(disponible_miembro=True),
        Q(fecha_acreditacion__year__gte=last_year)
        | Q(ultima_reacreditacion__year__gte=last_year)
    ).order_by('user__last_name')

    index_md = path.join(outdir, 'index_academicos.md')

    with open(index_md, 'w') as f:
        f.write(render_to_string('posgradmin/index_academicos.md',
                                 {'doctorado': doctorado,
                                  'maestria': maestria}).encode('utf-8'))

    academicos = [a for a in doctorado] + [a for a in maestria]
    for a in academicos:
        a_md = path.join(outdir,
                         'tutores',
                         '%s.md' % a.user.username)

        palabras_clave = a.palabras_clave.split("\n")

        with open(a_md, 'w') as f:
            f.write(render_to_string(
                'posgradmin/academico.md',
                {'a': a, 'palabras_clave': palabras_clave}).encode('utf8'))
