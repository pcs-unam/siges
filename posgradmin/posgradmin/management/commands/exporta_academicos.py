# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin.models import Academico
from django.template.loader import render_to_string
from os import path


class Command(BaseCommand):
    help = 'Exporta académicos a formato markdown para la página'

    def add_arguments(self, parser):
        parser.add_argument('outdir',
                            help='path al directorio donde escribir')

    def handle(self, *args, **options):
        export(options['outdir'])


def export(outdir):
    academicos = Academico.objects.filter(acreditacion__in=['D', 'M'])
    index_md = path.join(outdir, 'index_academicos.md')
    with open(index_md, 'w') as f:
        f.write(render_to_string('posgradmin/index_academicos.md',
                                 {'academicos': academicos}).encode('utf-8'))

    for a in academicos:
        a_md = path.join(outdir,
                         'tutores',
                         '%s.md' % a.user.username)

        palabras_clave = a.palabras_clave.split("\n")

        with open(a_md, 'w') as f:
            f.write(render_to_string(
                'posgradmin/academico.md',
                {'a': a, 'palabras_clave': palabras_clave}).encode('utf8'))
