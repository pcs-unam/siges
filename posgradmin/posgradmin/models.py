# coding: utf-8
import os
import pandas as pd
from pandas.plotting import parallel_coordinates

import datetime

from django.template.defaultfilters import slugify
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .settings import MEDIA_URL, \
    APP_PREFIX, MEDIA_ROOT, BASE_DIR

from wordcloud import WordCloud

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from tempfile import NamedTemporaryFile
from django.template.loader import render_to_string
from sh import rm
import subprocess
import pathlib
from pdfrw import PdfReader, PdfWriter, PageMerge


def nota_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(u'nota_%s_%s' % (instance.id, slugify(root) + ext))


class Nota(models.Model):
    asunto = models.CharField(max_length=100)
    nota = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User,
                              on_delete=models.CASCADE, null=True, blank=True)

    archivo = models.FileField(upload_to=nota_path,
                               null=True, blank=True)
    estado = models.CharField(max_length=40,
                              default='memo',
                              choices=((u"memo",
                                        u"memo"),
                                       ("denuncia",
                                        "denuncia"),
                                       (u"atendida",
                                        u"atendida"),
                                       (u"solicitud",
                                        u"solicitud")))


    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "%s, fecha: %s" % (self.autor,
                                      self.fecha.strftime("%Y-%m-%d %H:%M"))




class ConvocatoriaCurso(models.Model):
    year = models.PositiveSmallIntegerField("Año")
    semestre = models.PositiveSmallIntegerField(
        choices=((1, 1), (2, 2)))
    status = models.CharField(max_length=10,
            choices=[('abierta', 'abierta'),
                     ('rev CA', 'revisión CA'),
                     ('cerrada', 'cerrada')])

    notas = GenericRelation(Nota,
                           related_query_name='convocatoria_curso')


    def __str__(self):
        if self.status == 'abierta':
            status = '(abierta)'
        else:
            status = ''
        return u"%s-%s %s" % (self.year,
                              self.semestre,
                              status)

    class Meta:
        verbose_name_plural = "Convocatorias para cursos"
        unique_together = ('year', 'semestre')
        ordering = ['year', 'semestre', ]


class Institucion(models.Model):
    nombre = models.CharField("Institución u Organización", max_length=150)
    suborganizacion = models.CharField(
        "Dependencia, Entidad o Departamento", max_length=150)
    pais = models.CharField("País", max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    dependencia_UNAM = models.BooleanField(default=False)
    entidad_PCS = models.BooleanField(default=False)

    def __str__(self):
        if self.entidad_PCS:
            pcs = "(entidad del PCS)"
        else:
            pcs = ""
        return u"%s, %s %s" % (self.nombre, self.suborganizacion, pcs)

    class Meta:
        verbose_name_plural = "instituciones"
        unique_together = ('nombre', 'suborganizacion', 'estado', 'pais')
        ordering = ['nombre', 'suborganizacion', ]


class CampoConocimiento(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name_plural = "campos de conocimiento"


class LineaInvestigacion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name_plural = "líneas de investigación"


def headshot_path(instance, filename):
    extension = filename.split('.')[-1]
    return u'headshots/%s.%s' % (instance.user.id, extension)


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    curp = models.CharField("CURP. Si usted es extranjero(a) y no cuenta con "
                            + "este dato, ingresar la palabra extranjero(a)",
                            max_length=100)
    rfc = models.CharField("RFC. Si usted es extranjero(a) y no cuenta con "
                           + "este dato, ingresar la palabra extranjero(a)",
                           max_length=100)

    CVU = models.CharField(u"Número de CVU",
                           max_length=100, blank=True, null=True)

    telefono = models.CharField(max_length=100)
    telefono_movil = models.CharField(max_length=100, blank=True)

    direccion1 = models.CharField("dirección del lugar de trabajo",
                                  max_length=350)

    codigo_postal = models.PositiveSmallIntegerField(default=0)

    website = models.CharField(max_length=200, blank=True)

    genero = models.CharField(max_length=1, choices=(('M', 'masculino'),
                                                     ('F', 'femenino')))

    nacionalidad = models.CharField(max_length=100)

    fecha_nacimiento = models.DateField('fecha de nacimiento',
                                        blank=True, null=True)

    headshot = models.ImageField("fotografía",
                                 upload_to=headshot_path,
                                 blank=True, null=True)

    notas = GenericRelation(Nota,
                           related_query_name='perfil')


    def __str__(self):
        return u"%s" % self.user.get_full_name()

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name_plural = "Perfiles Personales"
        ordering = ['user__first_name', 'user__last_name', ]


    def asociado_PCS(self):
        for a in self.adscripcion_set.all():
            if a.institucion.entidad_PCS or a.asociacion_PCS:
                return True
        return False

    def adscripcion(self):
        return self.adscripcion_set.filter(asociacion_PCS=False)

    def adscripcion_ok(self):
        """
        si tiene adscripciones virtuales, debe tener una real tambien
        """

        if self.adscripcion_set.filter(asociacion_PCS=True).count() > 0:
            # ha registrado virtuales
            if self.adscripcion_set.filter(asociacion_PCS=False).count() > 0:
                # y reales
                return True
            else:
                # pero no reales
                return False
        else:
            # no ha registrado virtuales
            if self.adscripcion_set.count() > 0:
                # pero ha registrado
                return True
            else:
                # no ha registrado ninguna!
                return False

    def perfil_publico_anchor(self):
        return u"""<a href='%sinicio/perfil/publico/%s'>%s</a>""" % (
            APP_PREFIX,
            self.user.get_username(), self.__str__())

    def perfil_comite_anchor(self):
        return u"""<a href='%sinicio/perfil/comite/%s'>%s</a>""" % (
            APP_PREFIX,
            self.user.get_username(), self.__str__())



class Invitado(models.Model):
    nombre = models.CharField(max_length=333)
    correo = models.EmailField(blank=True, null=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class GradoAcademico(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    nivel = models.CharField(max_length=15,
                             choices=(('licenciatura', 'licenciatura'),
                                      ('maestria', 'maestria'),
                                      ('doctorado', 'doctorado')))

    grado_obtenido = models.CharField(max_length=100)

    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)

    fecha_obtencion = models.DateField("Fecha de obtención de grado")

    def __str__(self):
        return u"%s @ %s" % (self.grado_obtenido, self.institucion)

    class Meta:
        verbose_name_plural = "Grados académicos"
        ordering = ("-fecha_obtencion",)


class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cuenta = models.CharField(max_length=100)

    estado = models.CharField(
        max_length=25,
        choices=(
            ('inscrito', 'inscrito'),
            ('egresado', 'egresado'),
            ('graduado', 'graduado'),
            ('indeterminado', u'indeterminado'),
            ('baja', 'baja'),
            (u'suspensión 1 sem', u'suspensión 1 sem'),
            (u'suspensión 2 sem', u'suspensión 2 sem'),
            ('ausente', 'ausente'),
        ),
        null=True, blank=True)

    plan = models.CharField(
        max_length=20,
        choices=[("Maestría", "Maestría"),
                 ("Doctorado", "Doctorado")],
        default="Maestría"
    )

    doctorado_directo = models.BooleanField(default=False)
    opcion_titulacion = models.BooleanField("Opción a titulación",
                                            default=False)

    campo_conocimiento = models.ForeignKey(CampoConocimiento,
                                           blank=True, null=True,
                                           on_delete=models.CASCADE)
    lineas_investigacion = models.ForeignKey(LineaInvestigacion,
                                             blank=True, null=True,
                                             on_delete=models.CASCADE)


    notas = GenericRelation(Nota,
                           related_query_name='estudiante')


    class Meta:
        ordering = ['user__first_name', 'user__last_name', ]


    def ultimo_plan(self):
        if self.historial.count() > 0:
            h = self.historial.order_by('year', 'semestre').last()
            plan = h.plan
        else:
            plan = None

        return plan


    def ultimo_proyecto(self, plan=None):
        if plan is None:
            plan = self.ultimo_plan()

        if self.proyecto_set.filter(plan=plan).count() > 0:
            p = self.proyecto_set.filter(plan=plan).latest('fecha')
        else:
            p = None

        return p


    def ultimo_estado(self):
        if self.historial.count() > 0:
            h = self.historial.order_by('year', 'semestre').last()
            ultimo_estado = h.estado
        else:
            ultimo_estado = None

        return ultimo_estado


    def entidad(self):
        if self.historial.count() > 0:
            h = self.historial.filter(
                estado='inscrito').order_by('year', 'semestre').last()
            e = h.institucion
        else:
            e = None

        return e


    def comite_vigente(self):
        return self.comite(self.ultimo_plan())


    def comite(self, plan):
        if plan == 'Doctorado':
            tipos = ['M', 'T']
        elif plan == "Maestría":
            tipos = ['A', 'X', 'Y', 'Z']
        else:
            print(plan)

        if self.membresiacomite_set.filter(tipo__in=tipos).count() > 0:
            m = self.membresiacomite_set.filter(tipo__in=tipos).order_by('year', 'semestre').last()
            y = m.year
            s = m.semestre
            tutores = list(self.membresiacomite_set.filter(tipo__in=tipos, year=y, semestre=s))
            if plan == 'Doctorado':
                invitados = list(self.invitadomembresiacomite_set.filter(year=y, semestre=s))
            else:
                invitados = []
            return tutores + invitados
        else:
            return []

    def comite_maestria(self):
        return self.comite('Maestría')

    def comite_doctorado(self):
        return self.comite('Doctorado')

    def ultima_inscripcion(self):
        if self.historial.count() > 0:
            h = self.historial.filter(
                estado='inscrito').order_by('year', 'semestre').last()
            y = h.year
            s = h.semestre
            return f"{y}-{s}"
        else:
            return None


    def generacion(self, plan):
        if self.historial.filter(plan=plan).count() > 0:
            h = self.historial.filter(
                plan=plan).order_by('year', 'semestre').first()
            y = h.year
            s = h.semestre
            return f"{y}-{s}"
        else:
            return None

    def generacion_maestria(self):
        return self.generacion(plan="Maestría")

    def generacion_doctorado(self):
        return self.generacion(plan="Doctorado")


    def sede_administrativa(self, plan):
        return self.sedes.filter(plan=plan).first()

    def sede_adm_maestria(self):
        return self.sede_administrativa('Maestría')

    def sede_adm_doctorado(self):
        return self.sede_administrativa('Doctorado')


    def proyecto(self, plan):
        return self.proyecto_set.filter(plan=plan).last()

    def proyecto_maestria(self):
        return self.proyecto('Maestría')

    def proyecto_doctorado(self):
        return self.proyecto('Doctorado')



    def faltan_documentos(self):
        if self.user.gradoacademico_set.count() == 0:
            return True
        else:
            return False

    def __str__(self):
        return u"%s (%s) %s" % (self.user.get_full_name(),
                                self.cuenta,
                                self.estado)


    def perfil_plan(self, plan):
        if self.historial.filter(plan=plan).count == 0:
            return None

        return {
            'proyecto': self.ultimo_proyecto(plan),
            'sede': self.sedes.filter(plan=plan),
            'tema': (self.lineas_investigacion if plan == 'Doctorado'
                     else self.campo_conocimiento),
            'historial': self.historial.filter(
                plan=plan).order_by('year', 'semestre')
        }


    def ficha_a(self):
        return u"""<a href='%sestudiante/%s'>%s</a>""" % (APP_PREFIX,
                                                          self.cuenta,
                                                          self.cuenta)

    def as_a(self):
        return "<a href='%sinicio/usuario/%s/'>%s</a>" % (
            APP_PREFIX,
            self.user.id,
            self.user.get_full_name())


class Graduado(models.Model):
    estudiante = models.ForeignKey(Estudiante,
                                   related_name='graduaciones',
                                   on_delete=models.CASCADE)

    mencion_honorifica = models.BooleanField(default=False)
    medalla_alfonso_caso = models.BooleanField(u"Medalla Alfonso Caso",
                                               default=False)

    fecha = models.DateField("fecha de graduación",
                             default=datetime.date.today)

    year = models.PositiveSmallIntegerField("año",
                                            blank=True, null=True)
    semestre = models.PositiveSmallIntegerField(
        "semestre",
        choices=((1, 1),
                 (2, 2)))

    plan = models.CharField(
        max_length=20,
        choices=((u"Maestría", u"Maestría"),
                 (u"Doctorado", u"Doctorado")))

    folio_graduacion = models.CharField(u"Folio de acta de examen de grado",
                                        max_length=200, blank=True)

    modalidad_graduacion = models.CharField(
        max_length=35,
        default='-',
        choices=(
            ('-', '-'),
            ('tesis', 'tesis'),
            ('reporte técnico', 'reporte técnico'),
            ('artículo', u'artículo'),
            ('protocolo de investigación doctoral', 'protocolo de investigación doctoral'),
        ))

    notas = GenericRelation(Nota,
                            related_query_name='historial')


    def copia_estado_graduado(self):
        if self.estudiante.historial.filter(estado='graduado',
                                            plan=self.plan).count() == 0:
            h = Historial()
            h.estudiante = self.estudiante
            h.year = self.year
            h.semestre = self.semestre
            h.plan = self.plan
            h.estado = 'graduado'
            h.institucion = self.estudiante.entidad()
            h.save()

    def __str__(self):
        return f"{self.estudiante} {self.plan}"


class InvitadoJuradoGraduacion(models.Model):
    graduado = models.ForeignKey(Graduado, on_delete=models.CASCADE)
    invitado = models.ForeignKey(Invitado,
                                 on_delete=models.CASCADE)

    rol_asignado = models.CharField(
        max_length=25,
        default='D',
        choices=(
            ('presidente', 'presidente'),
            ('secretario', 'secretario'),
            ('vocal 1', 'vocal 1'),
            ('vocal', 'vocal'),
        )
    )

    rol_examen = models.CharField(
        max_length=25,
        default='D',
        choices=(
            ('presidente', 'presidente'),
            ('secretario', 'secretario'),
            ('vocal 1', 'vocal 1'),
            ('vocal', 'vocal'),
            ('ausente', 'ausente'),
        )
    )


    class Meta:
        verbose_name_plural = "Invitados en Jurados de Graduación"

    def __str__(self):
        return f"{self.graduado} {self.invitado}"



class MiembroJuradoGraduacion(models.Model):
    graduado = models.ForeignKey(Graduado,
                                 on_delete=models.CASCADE)
    academico = models.ForeignKey("Academico",
                                  on_delete=models.CASCADE)

    rol_asignado = models.CharField(
        max_length=25,
        default='D',
        choices=(
            ('presidente', 'presidente'),
            ('secretario', 'secretario'),
            ('vocal 1', 'vocal 1'),
            ('vocal', 'vocal'),
        )
    )

    rol_examen = models.CharField(
        max_length=25,
        default='D',
        choices=(
            ('presidente', 'presidente'),
            ('secretario', 'secretario'),
            ('vocal 1', 'vocal 1'),
            ('vocal', 'vocal'),
            ('ausente', 'ausente'),
        )
    )

    class Meta:
        verbose_name_plural = "Académicos en Jurados de Graduación"

    def __str__(self):
        return f"{self.graduado} {self.academico}"



class Sede(models.Model):
    estudiante = models.ForeignKey(Estudiante, related_name='sedes', on_delete=models.CASCADE)
    plan = models.CharField(
        max_length=20,
        choices=((u"Maestría", u"Maestría"),
                 (u"Doctorado", u"Doctorado")
                 ))
    sede = models.CharField(
        max_length=20,
        choices=(("CDMX", "CDMX"),
                 ("León", "León"),
                 ("Morelia (IIES)", "Morelia (IIES)"),
                 ("Morelia (ENES)", "Morelia (ENES)"),
                 ))

    class Meta:
        verbose_name_plural = "Sedes administrativas"
        unique_together = ('estudiante', 'plan')


    def __str__(self):
        return f"{self.sede}"



class Historial(models.Model):
    estudiante = models.ForeignKey(Estudiante, related_name='historial', on_delete=models.CASCADE)

    fecha = models.DateField("fecha del registro",
                             help_text=u"fecha del registro en la bitácora",
                             default=datetime.date.today)

    year = models.PositiveSmallIntegerField("año",
                                            blank=True, null=True)
    semestre = models.PositiveSmallIntegerField(
        "semestre",
        choices=((1, 1),
                 (2, 2)))

    estado = models.CharField(
        max_length=25,
        default='inscrito',
        choices=(
            ('inscrito', 'inscrito'),
            ('egresado', 'egresado'),
            ('graduado', 'graduado'),
            ('indeterminado', u'indeterminado'),
            ('baja', 'baja'),
            (u'suspensión 1 sem', u'suspensión 1 sem'),
            (u'suspensión 2 sem', u'suspensión 2 sem'),
            ('ausente', 'ausente'),
        ))

    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE,
                                    help_text=u"Institución de Inscripción",
                                    limit_choices_to={'entidad_PCS': True},
                                    blank=True, null=True)

    plan = models.CharField(
        max_length=20,
        choices=((u"Maestría", u"Maestría"),
                 (u"Doctorado", u"Doctorado")))


    permiso_trabajar = models.BooleanField("Permiso para trabajar",
                                           default=False)
    beca_descripcion = models.CharField(u"Descripción de Beca",
                                        max_length=200, blank=True)
    beca = models.BooleanField(default=False)

    notas = GenericRelation(Nota,
                            related_query_name='historial')


    class Meta:
        verbose_name_plural = "Historial"
        ordering = ['year', 'semestre']

    def __str__(self):
        return u"[%s] %s: %s" % (self.fecha, self.estudiante, self.plan)


class ApoyoMovilidad(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, help_text="Nombre de la actividad")

    fecha_solicitud = models.DateField("Fecha de solicitud", default=datetime.date.today)

    year = models.PositiveSmallIntegerField("año",
                                            blank=True, null=True)

    semestre = models.PositiveSmallIntegerField(
        "semestre",
        choices=((1, 1),
                 (2, 2)))

    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    internacional = models.BooleanField(default=True)
    ciudad = models.CharField(max_length=200, blank=True, null=True)
    pais = models.CharField(max_length=200, blank=True, null=True)

    monto_otorgado = models.DecimalField("Monto otorgado en pesos mexicanos", max_digits=8, decimal_places=2)

    tipo_apoyo = models.CharField(
        max_length=255,
        default='paep',
        choices=(
            ('paep', 'PAEP'),
            ('larga duración', 'Larga Duración'),
            ('otro', 'otro')    # ver como registrar otro
        ))

    tipo_actividad = models.CharField(
        max_length=25,
        default='estancia',
        choices=(
            ('curso', 'curso'),
            ('congreso', 'congreso'),
            ('estancia', 'estancia'),
            ('encuentro', 'encuentro'),
            ('otro', 'otro'),
        ))

    estado = models.CharField(
        max_length=25,
        default='solicitado',
        choices=(
            ('solicitado', 'solicitado'),
            ('reporte entregado', 'reporte entregado'),
            ('cancelado', 'cancelado'),
        ))

    notas = GenericRelation(Nota,
                            related_query_name='estancia')

    class Meta:
        verbose_name_plural = "Apoyos para Movilidad"

    def __str__(self):
        return u"%s | %s | %s" % (self.estudiante,
                                self.tipo_apoyo,
                                self.nombre)


class Sesion(models.Model):
    fecha = models.DateField()
    descripcion = models.CharField(max_length=100,
                                   default="sesión ordinaria")
    # guardar markdown
    minuta = models.TextField(blank=True)

    def as_a(self):
        return u"""<a href='%sinicio/sesiones/%s/'>%s %s</a>""" % (
            APP_PREFIX,
            self.id, self.fecha, self.descripcion)

    def __str__(self):
        return u'%s, %s' % (self.fecha,
                            self.descripcion)

    class Meta:
        verbose_name_plural = "Sesiones"


class Proyecto(models.Model):
    fecha = models.DateField()
    titulo = models.CharField(max_length=200)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    plan = models.CharField(
        max_length=20,
        choices=[("Maestría", "Maestría"),
                 ("Doctorado", "Doctorado")],
        default="Maestría"
    )

    class Meta:
        ordering = ['-fecha', ]

    def __str__(self):
        return self.titulo


def anexo_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(u'solicitudes/%s/%s' % (instance.solicitud.id,
                                                slugify(root) + ext))



def anexo_expediente_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(u'expediente/%s/%s' % (instance.user.get_username(),
                                               slugify(root) + ext))


class AnexoExpediente(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to=anexo_expediente_path)

    def url(self):
        return u"%s/expediente/%s/%s" % (MEDIA_URL,
                                         self.user.get_username(),
                                         os.path.basename(self.archivo.path))

    def basename(self):
        return os.path.basename(self.archivo.file.name)

    def __str__(self):
        return self.basename()

    class Meta:
        verbose_name_plural = "Expedientes"


def anexo_academico_CV_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(u'perfil-academico/%s/cv_%s' % (instance.id,
                                                        slugify(root) + ext))


def anexo_academico_solicitud_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(
        u'perfil-academico/%s/solicitud_%s' % (instance.id,
                                               slugify(root) + ext))


def grado_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(u'perfil-academico/%s/ultimo_grado_%s' % (
        instance.id,
        slugify(root) + ext))


class Academico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    anexo_CV = models.FileField(u"CV en extenso",
                                upload_to=anexo_academico_CV_path,
                                blank=True, null=True)

    ultimo_grado = models.FileField(u"Copia de último grado académico",
                                    upload_to=grado_path,
                                    blank=True, null=True)

    anexo_solicitud = models.FileField(
        u"Carta de solicitud de acreditación como tutor",
        upload_to=anexo_academico_solicitud_path,
        blank=True, null=True)

    estimulo_UNAM = models.CharField(u"Estímulo UNAM",
                                     max_length=15,
                                     default='ninguno',
                                     choices=(('ninguno', 'ninguno'),
                                              ('Equivalencia', 'Equivalencia'),
                                              ('PEPASIG', 'PEPASIG'),
                                              ('PEI', 'PEI'),
                                              ('PEDMETI', 'PEDMETI'),
                                              ('PRIDE A', 'PRIDE A'),
                                              ('PRIDE B', 'PRIDE B'),
                                              ('PRIDE C', 'PRIDE C'),
                                              ('PRIDE D', 'PRIDE D')))
    nivel_SNI = models.CharField(u"Nivel SNI",
                                 max_length=15,
                                 default='sin SNI',
                                 blank=True, null=True,
                                 choices=(('sin SNI', 'sin SNI'),
                                          ('I', 'I'),
                                          ('II', 'II'),
                                          ('III', 'III'),
                                          ('C', 'C'),
                                          ('E', 'E')))
    CVU = models.CharField(u"Número de CVU",
                           max_length=100, blank=True, null=True,
                           help_text="movido a Perfil Personal")

    numero_trabajador_unam = models.CharField(u"Número de trabajador (UNAM)",
                                              max_length=100,
                                              blank=True, null=True)

    comite_academico = models.BooleanField(default=False)

    fecha_acreditacion = models.DateField(blank=True, null=True, default=datetime.date.today)

    acreditacion = models.CharField(
        max_length=25,
        choices=(
            ('candidato', 'candidato'),
            ('candidato profesor', 'candidato profesor'),
            ('no acreditado', 'no acreditado'),
            (u'información incompleta', u'información incompleta'),
            ('por reacreditar D', 'por reacreditar D'),
            ('por reacreditar M', 'por reacreditar M'),
            ('baja', 'baja'),
            ('condicionado', 'condicionado'),
            ('P', 'P'),
            ('D', 'D'),
            ('M', 'M'),
            ('MCT_M', 'MCT_M'),
            ('E', 'E')
        ))

    campos_de_conocimiento = models.ManyToManyField(
        CampoConocimiento,
        blank=True)
    lineas_de_investigacion = models.ManyToManyField(
        LineaInvestigacion,
        blank=True)

    # Resumen Curricular

    # formacion de estudiantes
    tesis_doctorado = models.PositiveSmallIntegerField(
        u"""Cantidad total de participaciones como tutor principal de
        estudiantes graduados de nivel Doctorado""",
        null=True, blank=True)
    tesis_doctorado_5 = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como tutor principal de
        estudiantes graduados de nivel Doctorado en los últimos 5 años""",
        null=True, blank=True)

    tesis_maestria = models.PositiveSmallIntegerField(
        u"""Cantidad total participaciones como tutor principal de estudiantes
        graduados de nivel Maestría""",
        null=True, blank=True)
    tesis_maestria_5 = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como tutor principal de estudiantes
           graduados de nivel Maestría en los últimos 5 años""",
        null=True, blank=True)

    tesis_licenciatura = models.PositiveSmallIntegerField(
        u"""Cantidad total de participaciones como tutor principal de
        estudiantes graduados de nivel Licenciatura""",
        null=True, blank=True)
    tesis_licenciatura_5 = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como tutor principal de
        estudiantes " graduados a nivel Licenciatura en los últimos 5
        años""", null=True, blank=True)

    tutor_principal_otros_programas = models.TextField(
        u"""Nombres de los otros programas de posgrado en los que participa""",
        blank=True)

    comite_doctorado_otros = models.PositiveSmallIntegerField(
        u"""Cantidad total de participaciones como miembro de comité
        tutor (no tutor principal) de estudiantes graduados de nivel
        doctorado.""", null=True, blank=True)

    comite_maestria_otros = models.PositiveSmallIntegerField(
        u"""Cantidad total de participaciones como miembro de comité
        tutor (no tutor principal) de estudiantes graduados de nivel
        maestría.""", null=True, blank=True)

    # en el PCS
    participacion_tutor_doctorado = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como tutor principal en el Posgrado en
           Ciencias de la Sostenibilidad a nivel doctorado""",
        null=True, blank=True)

    participacion_tutor_maestria = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como tutor principal en el
        Posgrado en Ciencias de la Sostenibilidad a nivel maestría""",
        null=True, blank=True)

    participacion_comite_doctorado = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como miembro de comité tutor (no tutor
        principal) en el Posgrado en Ciencias de la Sostenibilidad a
        nivel doctorado""",
        null=True, blank=True)

    participacion_comite_maestria = models.PositiveSmallIntegerField(
        u"""Cantidad de participaciones como miembro de comité tutor (no tutor
         principal) en el Posgrado en Ciencias de la Sostenibilidad a
         nivel maestría""",
        null=True, blank=True)

    otras_actividades = models.TextField(
        u"""Si no cuenta con estudiantes graduados, indique si cuenta con
        otras actividades académicas como estancias de investigación,
        seminarios de titulación, etc.""", blank=True, null=True)

    # publicaciones
    articulos_internacionales = models.PositiveSmallIntegerField(
        u"Cantidad total de artículos publicados en revistas internacionales",
        null=True, blank=True)

    articulos_internacionales_5 = models.PositiveSmallIntegerField(
        u"Cantidad de artículos publicados en revistas internacionales "
        + u"durante los últimos 5 años",
        null=True, blank=True)

    articulos_nacionales = models.PositiveSmallIntegerField(
        u"Cantidad total de artículos publicados en revistas nacionales",
        null=True, blank=True)

    articulos_nacionales_5 = models.PositiveSmallIntegerField(
        u"Cantidad de artículos publicados en revistas nacionales "
        + u"durante los últimos 5 años",
        null=True, blank=True)

    libros = models.PositiveSmallIntegerField(
        u"Cantidad total de libros publicados",
        null=True, blank=True)

    libros_5 = models.PositiveSmallIntegerField(
        u"Cantidad de libros publicados durante los últimos 5 años",
        null=True, blank=True)

    capitulos = models.PositiveSmallIntegerField(
        u"Cantidad total de capítulos de libro publicados",
        null=True, blank=True)

    capitulos_5 = models.PositiveSmallIntegerField(
        u"Cantidad de capítulos de libro publicados durante los últimos 5 años",
        null=True, blank=True)

    top_5 = models.TextField(
        u"""Cinco publicaciones más destacadas en temas relacionados con las
        Ciencias de la Sostenibilidad.  De ser posible incluir ligas
        para acceder a las publicaciones.""",
        blank=True)

    otras_publicaciones = models.TextField(
        u"""Si su productividad académica no se ve reflejada en las
        publicaciones anteriores, indique si cuenta con otros
        productos como por ejemplo informes técnicos, memorias
        técnicas, desarrollo de proyectos hasta nivel ejecutivo,
        planes y programas de desarrollo urbano, manuales, etc.""",
        null=True, blank=True
    )

    # Actividad profesional y de Investigación
    lineas = models.TextField(
        u"Temas de interés y/o experiencia en ciencias de la sostenibilidad, "
        + u"máximo 10, uno por renglón",
        blank=True)

    palabras_clave = models.TextField(
        u"Palabras clave de temas de interés y/o experiencia"
        + u"en ciencias de la sostenibilidad, máximo 10, una por renglón",
        blank=True)
    motivacion = models.TextField(
        u"Motivación para participar en el Programa, máximo 200 palabras",
        blank=True)
    proyectos_sostenibilidad = models.TextField(
        u"Principales proyectos relacionados con "
        + u"ciencias de la sostenibilidad durante los últimos cinco años, "
        + u"especificar si se es responsable o colaborador.",
        blank=True)
    proyectos_vigentes = models.TextField(
        u"Proyectos vigentes en los que pueden "
        + u"participar alumnos del PCS. Incluya fechas de terminación.",
        blank=True)

    # disponibilidad
    disponible_tutor = models.BooleanField(
        u"Disponible como tutor principal (dirección de alumnos)",
        default=True)

    disponible_miembro = models.BooleanField(
        u"Disponible como miembro de comité tutor (asesoría de alumnos)",
        default=True)

    # epílogo
    observaciones = models.TextField(blank=True)

    resumen_completo = models.BooleanField(u"perfil académico completo",
                                           default=False)

    perfil_personal_completo = models.BooleanField(default=False)

    semaforo_maestria = models.CharField(
        max_length=10, default="rojo",
        choices=(
            ('verde', 'verde'),
            ('amarillo', 'amarillo'),
            ('rojo', 'rojo')))

    semaforo_doctorado = models.CharField(
        max_length=10, default="rojo",
        choices=(
            ('verde', 'verde'),
            ('amarillo', 'amarillo'),
            ('rojo', 'rojo')))

    titulo_honorifico = models.CharField(u'Título honorífico (Dra., Mtro, Lic)',
        max_length=12, default='Lic.',
        null=True, blank=True,
        choices=(
            (u'Lic.',  u'Lic.'),
            (u'Mtro.', u'Mtro.'),
            (u'Mtra.', u'Mtra.'),
            (u'Dr.',   u'Dr.'),
            (u'Dra.',  u'Dra.')))

    notas = GenericRelation(Nota,
                            related_query_name='academico')


    def verifica_titulo_honorifico(self):
        if self.is_phd():
            if self.user.perfil.genero == 'M':
                self.titulo_honorifico = 'Dr.'
            else:
                self.titulo_honorifico = 'Dra.'

        elif self.is_msc():
            if self.user.perfil.genero == 'M':
                self.titulo_honorifico = u'Mtro.'
            else:
                self.titulo_honorifico = u'Mtra.'
        else:
            self.titulo_honorifico = u'Lic.'


    def copia_ultima_acreditacion(self):
        if self.acreditaciones.count() > 0:
            ultima = self.acreditaciones.latest('fecha')
            self.acreditacion = ultima.acreditacion
            self.fecha_acreditacion = ultima.fecha


    def is_phd(self):
        niveles = [deg.nivel
                   for deg in self.user.gradoacademico_set.all()]
        niveles = set(niveles)
        if 'doctorado' in niveles:
            return True
        else:
            return False

    def is_msc(self):
        niveles = [deg.nivel
                   for deg in self.user.gradoacademico_set.all()]
        niveles = set(niveles)
        if 'maestria' in niveles:
            return True
        else:
            return False

    def show_acreditacion(self):
        if self.acreditacion == 'no acreditado':
            return 'no acreditado'
        elif self.acreditacion == 'E':
            return u"Comité tutor específico"
        elif (self.acreditacion == 'D'
              or self.acreditacion == 'PD'
              or self.acreditacion == 'NPD'):
            return "Maestría y Doctorado"
        elif self.acreditacion == "M":
            return "Maestría"
        else:
            return self.acreditacion

    def verifica_perfil_personal(self):
        ok = False
        if hasattr(self.user, 'perfil'):
            if self.user.gradoacademico_set.count() > 0:
                if self.user.perfil.adscripcion_ok():
                    ok = True
        return ok


    def verifica_resumen(self):
        if (self.carencias_general() == u""
            and self.carencias_resumen() == u""
            and self.carencias_actividad() == u""):
            return True
        else:
            return False


    def carencias_general(self):
        carencias = u""

        if self.CVU == "":
            carencias += u" - " + str(self._meta.get_field('CVU').verbose_name) + u"\n"

        if self.anexo_CV == "":
            carencias += u" - " + str(self._meta.get_field('anexo_CV').verbose_name) + u"\n"

        if self.anexo_solicitud == "":
            carencias += u" - " + str(self._meta.get_field('anexo_solicitud').verbose_name) + u"\n"

        if not self.ultimo_grado:
            carencias += u" - " + str(self._meta.get_field('ultimo_grado').verbose_name) + u"\n"

        return carencias



    def carencias_resumen(self):
        carencias = u""

        if self.tesis_licenciatura is None:
            carencias += u" - " + str(self._meta.get_field('tesis_licenciatura').verbose_name) + u"\n"

        if self.tesis_maestria is None:
            carencias += u" - " + str(self._meta.get_field('tesis_maestria').verbose_name) + u"\n"

        if self.tesis_doctorado is None:
            carencias += u" - " + str(self._meta.get_field('tesis_doctorado').verbose_name) + u"\n"

        if self.tesis_licenciatura_5 is None:
            carencias += u" - " + str(self._meta.get_field('tesis_licenciatura_5').verbose_name) + u"\n"

        if self.tesis_maestria_5 is None:
            carencias += u" - " + str(self._meta.get_field('tesis_maestria_5').verbose_name) + u"\n"

        if self.tesis_doctorado_5 is None:
            carencias += u" - " + str(self._meta.get_field('tesis_doctorado_5').verbose_name) + u"\n"

        if self.comite_doctorado_otros is None:
            carencias += u" - " + str(self._meta.get_field('comite_doctorado_otros').verbose_name) + u"\n"

        if self.comite_maestria_otros is None:
            carencias += u" - " + str(self._meta.get_field('comite_maestria_otros').verbose_name) + u"\n"

        # if self.acreditacion in ('D', 'M', 'E') and self.participacion_comite_maestria is None:
        #     carencias += u" - " + str(self._meta.get_field('participacion_comite_maestria').verbose_name) + u"\n"

        # if self.acreditacion in ('D', 'M', 'E') and self.participacion_tutor_maestria is None:
        #     carencias += u" - " + str(self._meta.get_field('participacion_tutor_maestria').verbose_name) + u"\n"

        # if self.acreditacion in ('D', 'M', 'E') and self.participacion_comite_doctorado is None:
        #     carencias += u" - " + str(self._meta.get_field('participacion_comite_doctorado').verbose_name) + u"\n"

        # if self.acreditacion in ('D', 'M', 'E') and self.participacion_tutor_doctorado is None:
        #     carencias += u" - " + str(self._meta.get_field('participacion_tutor_doctorado').verbose_name) + u"\n"

        if self.articulos_internacionales_5 is None:
            carencias += u" - " + str(self._meta.get_field('articulos_internacionales_5').verbose_name) + u"\n"

        if self.articulos_nacionales_5 is None:
            carencias += u" - " + str(self._meta.get_field('articulos_nacionales_5').verbose_name) + u"\n"

        if self.articulos_internacionales is None:
            carencias += u" - " + str(self._meta.get_field('articulos_internacionales').verbose_name) + u"\n"

        if self.articulos_nacionales is None:
            carencias += u" - " + str(self._meta.get_field('articulos_nacionales').verbose_name) + u"\n"

        if self.capitulos is None:
            carencias += u" - " + str(self._meta.get_field('capitulos').verbose_name) + u"\n"

        if self.capitulos_5 is None:
            carencias += u" - " + str(self._meta.get_field('capitulos_5').verbose_name) + u"\n"

        if self.libros is None:
            carencias += u" - " + str(self._meta.get_field('libros').verbose_name) + u"\n"

        if self.libros_5 is None:
            carencias += u" - " + str(self._meta.get_field('libros_5').verbose_name) + u"\n"

        if self.top_5 == "" or self.top_5 is None:
            carencias += u" - " + str(self._meta.get_field('top_5').verbose_name) + u"\n"

        return carencias



    def carencias_actividad(self):
        carencias = u""

        if self.lineas == "" or self.lineas is None:
            carencias += u" - " + str(self._meta.get_field('lineas').verbose_name) + u"\n"

        if self.palabras_clave == "" or self.palabras_clave is None:
            carencias += u" - " + str(self._meta.get_field('palabras_clave').verbose_name) + u"\n"

        if self.motivacion == "" or self.motivacion is None:
            carencias += u" - " + str(self._meta.get_field('motivacion').verbose_name) + u"\n"

        # if self.campos_de_conocimiento.count() == 0:
        #     carencias += u" - " + str(self._meta.get_field('campos_de_conocimiento').verbose_name) + u"\n"

        # if self.lineas_de_investigacion.count() == 0:
        #     carencias += u" - " + str(self._meta.get_field('lineas_de_investigacion').verbose_name) + u"\n"

        return carencias


    def as_a(self):
        icon = """<span class='glyphicon glyphicon-{icon}'
                        aria-hidden=true></span>"""
        icon.format(icon='thumbs-up')

        return u"""<a href='%sinicio/usuario/%s/'>%s %s</a>""" % (
            APP_PREFIX,
            self.user.id, icon, self.__str__())

    def perfil_publico_anchor(self):
        return u"""<a href='%sinicio/perfil/publico/%s'>%s</a>""" % (
            APP_PREFIX,
            self.user.get_username(), self.__str__())

    def perfil_comite_anchor(self):
        return u"""<a href='%sinicio/perfil/comite/%s'>%s</a>""" % (
            APP_PREFIX,
            self.user.get_username(), self.__str__())

    def nombre_completo(self):
        return self.__str__()

    def __str__(self):
        name = self.user.get_full_name()
        if not name:
            name = self.user.username

        return "%s" % name

    def publicaciones_5(self):
        try:
            return sum((self.articulos_internacionales_5,
                        self.articulos_nacionales_5,
                        self.libros_5,
                        self.capitulos_5))
        except TypeError:
            return 0

    def verifica_semaforo_maestria(self):
        # if not self.resumen_completo:
        #     return "rojo"
        try:
            if (
                    ((self.tesis_licenciatura
                      + self.tesis_maestria
                      + self.tesis_doctorado) >= 1
                     and self.publicaciones_5() >= 3)
                    or self.publicaciones_5() >= 5):
                if self.is_msc() or self.is_phd():
                    return "verde"
                else:
                    return "amarillo"

            if (self.otras_actividades
                or self.otras_publicaciones
                or ((self.comite_doctorado_otros
                      + self.comite_maestria_otros) >= 1
                     and self.publicaciones_5() >= 3)):
                return "amarillo"

            return "rojo"
        except TypeError:
            return "rojo"

    def verifica_semaforo_doctorado(self):
        if not self.carencias_resumen() == u"":
            return "rojo"

        if ((self.tesis_maestria >= 2
             or self.tesis_doctorado >= 1) and self.publicaciones_5() >= 5
            or
            ((self.tesis_maestria >= 1
              or self.tesis_doctorado >= 1)
             and
             self.publicaciones_5() >= 7)):
            if self.is_phd():
                return "verde"
            else:
                return "amarillo"

        if self.tesis_maestria >= 2 or self.tesis_doctorado >= 1:
            # alumnos bien
            if self.publicaciones_5() < 5 and self.otras_publicaciones:
                # publicaciones tal vez
                return "amarillo"

        return "rojo"

    def wc_resumen_academico(self):
        """ word cloud """

        if not self.verifica_resumen():
            return None

        wordcloud = WordCloud()

        wordcloud.background_color = 'white'

        with open(BASE_DIR + '/posgradmin/stopwords-es.txt', 'r',
                  encoding="utf-8") as f:
            for w in f.readlines():
                wordcloud.stopwords.add(w.strip())

        for w in self.user.get_full_name().split(' '):
            wordcloud.stopwords.add(w)

        wordcloud.stopwords.add('doi')
        wordcloud.stopwords.add('None')
        wordcloud.stopwords.add('http')
        wordcloud.stopwords.add('https')

        text = " ".join((str(self.top_5),
                         str(self.motivacion),
                         str(self.otras_actividades),
                         str(self.otras_publicaciones),
                         str(self.lineas),
                         str(self.palabras_clave),
                         str(self.proyectos_vigentes),
                         str(self.proyectos_sostenibilidad)))
        if not text.strip():
            return

        wordcloud.generate(text)

        fig = plt.figure(figsize=(8, 6), dpi=150)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')

        pc_path = '%s/perfil-academico/%s/' % (MEDIA_ROOT, self.id)
        if not os.path.isdir(pc_path):
            os.makedirs(pc_path)

        fig.tight_layout()
        plt.savefig(
            '%s/perfil-academico/%s/wordcloud.png'
            % (MEDIA_ROOT, self.id))

    def pc_resumen_academico(self):
        """ parallel coordinates del resumen academico """

        if not self.verifica_resumen():
            return None

        escala_sni = {'sin SNI': 0,
                      'I': 1,
                      'II': 2,
                      'III': 3,
                      'C': 4,
                      'E': 5}
        escala_estimulo = {
            'ninguno': 0,
            'Equivalencia': 1,
            'PEPASIG': 2,
            'PEI': 3,
            'PEDMETI': 4,
            'PRIDE A': 5,
            'PRIDE B': 6,
            'PRIDE C': 7,
            'PRIDE D': 8}


        avg_SNI = np.mean([escala_sni.get(a.nivel_SNI, 0)
                           for a in Academico.objects.all()])
        avg_estimulo_UNAM = np.mean([escala_estimulo.get(a.estimulo_UNAM, 0)
                                     for a in Academico.objects.all()])
        avg_licenciatura = np.mean([a.tesis_licenciatura
                                    for a in Academico.objects.filter(tesis_licenciatura__gt=0)])
        avg_licenciatura_5 = np.mean([a.tesis_licenciatura_5
                                      for a in Academico.objects.filter(tesis_licenciatura_5__gt=0)])
        avg_maestria = np.mean([a.tesis_maestria
                                for a in Academico.objects.filter(tesis_maestria__gt=0)])

        avg_maestria_5 = np.mean([a.tesis_maestria_5
                                  for a in Academico.objects.filter(tesis_maestria_5__gt=0)])
        avg_doctorado = np.mean([a.tesis_doctorado
                                 for a in Academico.objects.filter(tesis_doctorado__gt=0)])
        avg_doctorado_5 = np.mean([a.tesis_doctorado_5
                                   for a in Academico.objects.filter(tesis_doctorado_5__gt=0)])
        avg_comite_doctorado_otros = np.mean([a.comite_doctorado_otros
                                              for a in Academico.objects.filter(comite_doctorado_otros__gt=0)])
        avg_comite_maestria_otros = np.mean([a.comite_maestria_otros
                                             for a in Academico.objects.filter(comite_maestria_otros__gt=0)])
        avg_participacion_comite_maestria = np.mean([a.participacion_comite_maestria
                                                 for a in Academico.objects.filter(participacion_comite_maestria__gt=0)])
        avg_participacion_tutor_maestria = np.mean([a.participacion_tutor_maestria
                                                    for a in Academico.objects.filter(participacion_tutor_maestria__gt=0)])
        avg_participacion_comite_doctorado = np.mean([a.participacion_comite_doctorado
                                                      for a in Academico.objects.filter(participacion_comite_doctorado__gt=0)])

        avg_participacion_tutor_doctorado = np.mean([a.participacion_tutor_doctorado
                                                     for a in Academico.objects.filter(participacion_tutor_doctorado__gt=0)])
        avg_articulos_internacionales_5 = np.mean([a.articulos_internacionales_5
                                                   for a in Academico.objects.filter(articulos_internacionales_5__gt=0)])
        avg_articulos_nacionales_5 = np.mean([a.articulos_nacionales_5
                                              for a in Academico.objects.filter(articulos_nacionales_5__gt=0)])

        avg_articulos_internacionales = np.mean([a.articulos_internacionales
                                                 for a in Academico.objects.filter(articulos_internacionales__gt=0)])
        avg_articulos_nacionales = np.mean([a.articulos_nacionales
                                            for a in Academico.objects.filter(articulos_nacionales__gt=0)])
        avg_capitulos = np.mean([a.capitulos
                                 for a in Academico.objects.filter(capitulos__gt=0)])
        avg_capitulos_5 = np.mean([a.capitulos_5
                                   for a in Academico.objects.filter(capitulos_5__gt=0)])
        avg_libros = np.mean([a.libros
                              for a in Academico.objects.filter(libros__gt=0)])
        avg_libros_5 = np.mean([a.libros_5
                                for a in Academico.objects.filter(libros_5__gt=0)])
        avg_gradoacademico = np.mean([a.user.gradoacademico_set.count()
                                      for a in Academico.objects.all()])



        df = pd.DataFrame({
            u'académico': [self.user.get_full_name(), 'avg'],
            u'SNI': [escala_sni.get(self.nivel_SNI, 0), avg_SNI, ],
            u'estímulo UNAM': [escala_estimulo.get(self.estimulo_UNAM, 0), avg_estimulo_UNAM],
            u"licenciatura": [self.tesis_licenciatura, avg_licenciatura],
            u"licenciatura últimos 5 años": [
                self.tesis_licenciatura_5, avg_licenciatura_5],
            u"maestría": [self.tesis_maestria, avg_maestria],
            u"maestría 5": [self.tesis_maestria_5, avg_maestria_5],
            u"doctorado": [self.tesis_doctorado, avg_doctorado],
            u"doctorado 5": [self.tesis_doctorado_5, avg_doctorado_5],
            u"comité doctorado otros programas": [
                self.comite_doctorado_otros, avg_comite_doctorado_otros],
            u"comité maestría otros programas": [
                self.comite_maestria_otros, avg_comite_maestria_otros],
            u"participación comite maestría": [
                self.participacion_comite_maestria, avg_participacion_comite_maestria],
            u"participación tutor maestría": [
                self.participacion_tutor_maestria, avg_participacion_tutor_maestria],
            u"participación comite doctorado": [
                self.participacion_comite_doctorado, avg_participacion_comite_doctorado],
            u"participación tutor doctorado": [
                int(self.participacion_tutor_doctorado) if self.participacion_tutor_doctorado is not None else 0,
                avg_participacion_tutor_doctorado],
            u"artículos internacionales últimos 5 años": [
                self.articulos_internacionales_5, avg_articulos_internacionales_5],
            u"artículos nacionales últimos 5 años": [
                self.articulos_nacionales_5, avg_articulos_nacionales_5],
            u"artículos internacionales": [self.articulos_internacionales, avg_articulos_internacionales],
            u"artículos nacionales": [self.articulos_nacionales, avg_articulos_nacionales],
            u"capítulos": [self.capitulos, avg_capitulos],
            u"capítulos últimos 5 años": [self.capitulos_5, avg_capitulos_5],
            u"libros": [self.libros, avg_libros],
            u"libros últimos 5 años": [self.libros_5, avg_libros_5],
            u'grados académicos': [self.user.gradoacademico_set.count(), avg_gradoacademico],
            },
            columns=[u'académico',
                     u'SNI',
                     u'estímulo UNAM',
                     u"licenciatura",
                     u"licenciatura últimos 5 años",
                     u"maestría",
                     u"maestría 5",
                     u"doctorado",
                     u"doctorado 5",
                     u"comité doctorado otros programas",
                     u"comité maestría otros programas",
                     u"participación comite maestría",
                     u"participación tutor maestría",
                     u"participación comite doctorado",
                     u"participación tutor doctorado",
                     u"artículos internacionales últimos 5 años",
                     u"artículos nacionales últimos 5 años",
                     u"artículos internacionales",
                     u"artículos nacionales",
                     u"capítulos",
                     u"capítulos últimos 5 años",
                     u"libros",
                     u"libros últimos 5 años",
                     u'grados académicos']
        )

        fig, ax = plt.subplots()
        # rectangulo estudiantes
        max_grad = max([
            df[u"licenciatura"][0],
            df[u"maestría"][0],
            df[u"doctorado"][0],
            ])
        ax.add_patch(
            patches.Rectangle(
                (3, 0), 5, max_grad,
                color='orchid', alpha=0.25, linewidth=0))

        # rectangulo para publicaciones
        max_pub = max([
            df[u'capítulos'][0],
            df[u'libros'][0],
            df[u"artículos nacionales"][0],
            df[u"artículos internacionales"][0],
        ])
        ax.add_patch(
            patches.Rectangle(
                (15, 0), 7, max_pub,
                color='deepskyblue', alpha=0.25, linewidth=0))

        parallel_coordinates(df, u'académico', color=['deeppink', 'grey'])

        legend = ax.legend()
        legend.remove()

        plt.xticks(rotation=90)

        # plt.ylim(0, 150)

        fig.tight_layout()
        pc_path = '%s/perfil-academico/%s/' % (MEDIA_ROOT, self.id)
        if not os.path.isdir(pc_path):
            os.makedirs(pc_path)
        plt.savefig(
            '%s/perfil-academico/%s/pc_resumen_academico.png'
            % (MEDIA_ROOT, self.id))


    class Meta:
        verbose_name_plural = "Académicos"
        ordering = ['user__first_name', 'user__last_name', ]



class Acreditacion(models.Model):

    academico = models.ForeignKey(Academico, related_name="acreditaciones", on_delete=models.CASCADE)
    fecha = models.DateField(default=datetime.date.today)
    comentario = models.CharField(max_length=400,
                                  null=True, blank=True)
    acreditacion = models.CharField(
        max_length=25,
        default='candidato',
        choices=(
            ('candidato', 'candidato'),
            ('candidato profesor', 'candidato profesor'),
            ('no acreditado', 'no acreditado'),
            (u'información incompleta', u'información incompleta'),
            ('por reacreditar D', 'por reacreditar D'),
            ('por reacreditar M', 'por reacreditar M'),
            ('baja', 'baja'),
            ('condicionado', 'condicionado'),
            ('P', 'P'),
            ('D', 'D'),
            ('M', 'M'),
            ('MCT_M', 'MCT_M'),
            ('E', 'E')
        ))

    def __str__(self):
        return self.acreditacion

    class Meta:
        verbose_name_plural = "acreditaciones"
        ordering = ['fecha', ]


    def genera_carta(self):
        if self.acreditacion in ('D', 'M', 'MCT_M'):

            if self.academico.user.gradoacademico_set.filter(nivel='doctorado').count() > 0:
                if self.academico.user.perfil.genero == 'M':
                    dr = 'Dr. '
                else:
                    dr = 'Dra. '
            else:
                dr = ""

            outdir = '%s/expediente/%s/' % (MEDIA_ROOT, self.academico.user.username)
            pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

            tmpname = 'cartaplain_%s.pdf' % self.acreditacion

            with open(outdir + tmpname + '.md', 'w', encoding='utf8') as f:
                f.write(
                    render_to_string('posgradmin/carta_acreditacion.md',
                                     {'fecha': datetime.date.today(),
                                      'ac': self,
                                      'dr': dr,
                                      'firma': BASE_DIR + '/docs/firma.png'}))

            os.chdir(outdir)
            subprocess.run(["pandoc", outdir + tmpname + '.md',
                            "--to", "latex",
                            "--output", outdir + tmpname])

            C = PdfReader(outdir + tmpname)
            M = PdfReader(BASE_DIR + '/docs/membrete_pcs.pdf')
            w = PdfWriter()
            merger = PageMerge(M.pages[0])
            merger.add(C.pages[0]).render()

            pathlib.Path(outdir + tmpname).unlink()
            pathlib.Path(outdir + tmpname + '.md').unlink()

            final_name = tmpname.replace('cartaplain', 'carta_acreditacion')
            w.write(outdir + final_name, M)

            anexo = AnexoExpediente(user=self.academico.user,
                                    fecha=datetime.datetime.now())
            anexo.archivo.name = 'expediente/%s/%s' % (self.academico.user.username, final_name)
            anexo.save()


class InvitadoMembresiaComite(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    invitado = models.ForeignKey(Invitado,
                                 on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField("Año")
    semestre = models.PositiveSmallIntegerField(
        choices=((1, 1), (2, 2)))
    tipo = models.CharField(
        max_length=25,
        default='D',
        choices=(
            ('AEM', 'Asesor externo maestría'),
            ('AED', 'Asesor Externo Doctorado'),
        ))

    class Meta:
        verbose_name_plural = "Invitados en Comités Tutorales"
        ordering = ['year', 'semestre' ]

    def __str__(self):
        return "%s : %s %s-%s: %s" % (self.estudiante,
                                  self.invitado,
                                  self.year,
                                  self.semestre,
                                  self.tipo)


class MembresiaComite(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Academico,
                              on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField("Año")
    semestre = models.PositiveSmallIntegerField(
        choices=((1, 1), (2, 2)))
    tipo = models.CharField(
        max_length=25,
        default='D',
        choices=(
            ('TPD', 'Tutor(a) principal de Doctorado'),
            ('CD', 'Cotutor(a) de Doctorado'),
            ('MCD', 'Miembro de comité de Doctorado'),
            ('TPM', 'Tutor(a) principal de Maestría'),
            ('CM', 'Cotutor(a) de Maestría'),
            ('MCM', 'Miembro de comité de Maestría'),
        )
    )

    class Meta:
        verbose_name_plural = "Membresías de Comités Tutorales"
        ordering = ['year', 'semestre' ]

    def __str__(self):
        return "%s : %s %s-%s: %s" % (self.estudiante,
                                  self.tutor,
                                  self.year,
                                  self.semestre,
                                  self.tipo)



class Adscripcion(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)

    catedra_conacyt = models.BooleanField(default=False)
    nombramiento = models.CharField(max_length=50)
    anno_nombramiento = models.PositiveSmallIntegerField("año de nombramiento")

    asociacion_PCS = models.BooleanField(
        "sólo para asociación con el PCS",
        default=False)

    class Meta:
        verbose_name_plural = "Adscripciones"

    def __str__(self):
        if self.asociacion_PCS:
            asoc = u"(sólo para asociación con el Posgrado)"
        else:
            asoc = ""
        return u"%s %s" % (self.institucion,
                           asoc)


def curso_path(instance, filename):
    (root, ext) = os.path.splitext(filename)
    return os.path.join(u'cursos/%s/%s' % (instance.id,
                                           slugify(root) + ext))


class Asignatura(models.Model):
    asignatura = models.CharField(max_length=200)

    clave = models.CharField(max_length=20, blank=True, null=True)

    creditos = models.PositiveSmallIntegerField(default=0)

    horas = models.PositiveSmallIntegerField(default=0)

    campos_de_conocimiento = models.ManyToManyField(
        CampoConocimiento,
        blank=True)

    tipo = models.CharField(max_length=40,
                            choices=((u"Obligatoria",
                                      "Obligatoria"),
                                     (u"Obligatorias por campo",
                                      u"Obligatorias por campo"),
                                     (u"Optativa",
                                      u"Optativa"),
                                     (u"Seminario de Doctorado",
                                      u"Seminario de Doctorado")))

    estado = models.CharField(max_length=40,
                              default='propuesta',
                              choices=((u"propuesta",
                                        u"propuesta"),
                                       (u"rechazada",
                                        u"rechazada"),
                                       (u"aceptada",
                                        u"aceptada")))

    programa = models.FileField("Formato de curso nuevo completo.",
                                upload_to=curso_path,
                                blank=True, null=True)

    proponente = models.ForeignKey(User,
                                   on_delete=models.CASCADE, null=True, blank=True)


    notas = GenericRelation(Nota,
                            related_query_name='asignatura')


    class Meta:
        ordering = ['asignatura', 'clave', ]

    def programa_url(self):
        if self.programa:
            return self.programa.url
        else:
            return None


    def get_asignatura(self):
        return u'%s' % self.asignatura


    def __str__(self):
        return u'%s (%s)' % (self.asignatura,
                                self.tipo)


class Curso(models.Model):
    convocatoria = models.ForeignKey(ConvocatoriaCurso, on_delete=models.CASCADE, null=True)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    grupo = models.CharField(max_length=20, blank=True, null=True)
    year = models.PositiveSmallIntegerField("Año")
    semestre = models.PositiveSmallIntegerField(
        choices=((1, 1), (2, 2)))
    entidad = models.CharField(max_length=20,
                               blank=True, null=True,
                               choices=(('3', '3'),
                                        ('600', '600'),
                                        ('700', '700')))
    sede = models.CharField(max_length=80,
                            blank=True, null=True,
                            choices=(
                                (u'en línea', u'en línea'),
                                ('CDMX', 'CDMX'),
                                ('Morelia', 'Morelia'),
                                (u'León', u'León')))

    profesores = models.TextField("Profesores", blank=True, null=True)
    contacto = models.TextField("Contacto", blank=True, null=True)

    academicos = models.ManyToManyField(Academico, help_text="Profesores que impartirán el curso.")

    aula = models.CharField(max_length=80, blank=True, null=True)
    horario = models.CharField(max_length=300, blank=True, null=True, help_text="Día(s) y horarios.")

    intersemestral = models.BooleanField(default=False)

    status = models.CharField(max_length=10,
                              default='solicitado',
                              choices=[('solicitado', 'solicitado'),
                                       ('aceptado', 'aceptado'),
                                       ('rechazado', 'rechazado'),
                                       ('cancelado', 'cancelado'),
                                       ('publicado', 'publicado'),
                                       ('concluido', 'concluido'),])

    observaciones_profesores = models.TextField(blank=True, help_text="Observaciones de profesores")

    notas = GenericRelation(Nota,
                            related_query_name='curso')


    def genera_constancias(self):
        if self.status == 'concluido':


            outdir = '%s/cursos/%s/' % (MEDIA_ROOT, self.id)
            pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

            tmpname = 'cursoplain_profesores.pdf'

            with open(outdir + tmpname + '.md', 'w', encoding='utf-8') as f:
                print(f.name)
                f.write(render_to_string('posgradmin/constancia_curso_profesores.md',
                                         {'fecha': datetime.date.today(),
                                          'firma': BASE_DIR + '/docs/firma.png',
                                          'academicos': list(self.academicos.all()),
                                          'curso': self}))

            final_name = tmpname.replace('cursoplain', 'constancia_curso')

            os.chdir(outdir)
            subprocess.run(["pandoc",
                            outdir + tmpname + '.md',
                            "--pdf-engine=xelatex",
                            "--to",'latex',
                            "--output", outdir + tmpname])

            C = PdfReader(outdir + tmpname)
            M = PdfReader(BASE_DIR + '/docs/membrete_pcs.pdf')
            w = PdfWriter()
            merger = PageMerge(M.pages[0])
            merger.add(C.pages[0]).render()

            pathlib.Path(outdir + tmpname).unlink()
            pathlib.Path(outdir + tmpname + '.md').unlink()

            w.write(outdir + final_name, M)


    class Meta:
        verbose_name_plural = "Cursos"
        ordering = ['asignatura', ]

    def __str__(self):
        return u'%s, %s-%s' % (self.asignatura,
                               self.year,
                               self.semestre)
