# coding: utf-8
from django.core.management.base import BaseCommand
from posgradmin.models import Curso
from django.template.loader import render_to_string
from os import path
from datetime import datetime
import random
from sh import mkdir
from django.utils.text import slugify
import argparse


class Command(BaseCommand):
    help = u'Exporta cursos a formato markdown para la página'

    def add_arguments(self, parser):
        parser.add_argument('--cursos',
                            type=argparse.FileType('r'),
                            help='path a la pagina principal de cursos')

        parser.add_argument('--outdir',
                            required=True,
                            help='path al directorio donde escribir')

    def handle(self, *args, **options):
        export(options['cursos'], options['outdir'])


def export(cursos, outdir):

    mkdir('-p', outdir)
    tipos=[(u"Cursos obligatorios", 'Obligatoria'),
           (u"Cursos obligatorios por campo", 'Obligatorias por campo'),
           (u"Cursos optativos", 'Optativa'),
           (u"Seminarios de Doctorado", u"Seminario de Doctorado")
    ]
    sedes=['CDMX',
           'Morelia',
           u'León',]

    index = cursos.read()
    cursos_path = cursos.name
    cursos.close()
    
    for tipo in tipos:
        for sede in sedes:
            cursos = Curso.objects.filter(
                activo=True).filter(
                    asignatura__tipo=tipo[1]).filter(
                        sede=sede).order_by('asignatura__asignatura')
            if cursos:
                cursos_md = u"\n\n## %s %s\n\n" % (tipo[0], sede)
                for c in cursos:
                    curso_slug = slugify(c.asignatura.asignatura
                                         + '_'
                                         + c.sede)
                    cursos_md += " - [%s](/cursos/%s/)\n" % (c.asignatura.asignatura, curso_slug)
                index = index.replace("<!-- " + slugify("%s %s" % (tipo[0], sede)) + " -->",
                                      cursos_md)

    with open(cursos_path, 'w') as f:
        f.write(index)
    
    # crear una página por curso
    for c in Curso.objects.filter(activo=True):
        # mkdir('-p', path.join(outdir, ''))

        if c.sede is None:
            sede = ""
        else:
            sede = c.sede
            
        curso_slug = slugify(c.asignatura.asignatura
                             + '_'
                             + sede)

        c_md = path.join(outdir,
                         '%s.md' % curso_slug)

        with open(c_md, 'w') as f:
            f.write(render_to_string(
                'posgradmin/curso.md',
                {'curso': c,
                 'curso_slug': curso_slug,
                 'academicos': ["<a href='mailto:%s'>%s</a>" % (p.user.email, p) for p in c.academicos.all()],
                 'pleca': random.randint(0, 19)                 
                 }))
