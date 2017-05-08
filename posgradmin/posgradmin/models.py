# coding: utf-8

from django.db import models

from django.contrib.auth.models import User


class Institucion(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15,
                            choices=(('UNAM', 'UNAM'),
                                     ('Sector Salud', 'Sector Salud'),
                                     ('Hospitales', 'Hospitales'),
                                     ('Gobierno', 'Gobierno'),
                                     ('Universidad', 'Universidad'),
                                     ('Otro', 'otro')))

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name_plural = "instituciones"


class Entidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name_plural = "entidades"


class CampoConocimiento(models.Model):
    nombre = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name_plural = "campos de conocimiento"


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    CURP = models.CharField(max_length=100)
    RFC = models.CharField(max_length=100)

    telefono = models.CharField(max_length=100)
    telefono_movil = models.CharField(max_length=100, blank=True)

    direccion1 = models.CharField("direccion linea 1", max_length=150)
    direccion2 = models.CharField("direccion linea 2", max_length=150)
    codigo_postal = models.PositiveSmallIntegerField()

    email2 = models.EmailField(max_length=200, blank=True)
    website = models.CharField(max_length=200, blank=True)

    genero = models.CharField(max_length=1, choices=(('M', 'masculino'),
                                                     ('F', 'femenino'),
                                                     ('N', 'no especificado')))

    nacionalidad = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField('date published')

    def __unicode__(self):
        return u"%s" % self.user

    class Meta:
        verbose_name_plural = "Perfiles"


class GradoAcademico(models.Model):
    user = models.ForeignKey(User)

    grado = models.CharField(max_length=15,
                             choices=(('licenciatura', 'licenciatura'),
                                      ('maestria', 'maestria'),
                                      ('doctorado', 'doctorado')))

    grado_obtenido = models.CharField(max_length=100)

    institucion = models.ForeignKey(Institucion)
    facultad = models.CharField(max_length=100)

    fecha_titulacion = models.DateField()
    promedio = models.DecimalField(max_digits=4, decimal_places=2)

    def __unicode__(self):
        return u"%s @ %s" % (self.grado_obtenido, self.institucion)

    class Meta:
        verbose_name_plural = "Grados académicos"


class Academico(models.Model):
    user = models.ForeignKey(User)

    nivel_pride = models.CharField(max_length=15, choices=(('A', 'A'),
                                                           ('B', 'B'),
                                                           ('C', 'C')))
    nivel_SNI = models.CharField(max_length=15, choices=(('I', 'I'),
                                                         ('II', 'II'),
                                                         ('III', 'III'),
                                                         ('C', 'C'),
                                                         ('E', 'E')))
    CVU = models.CharField(max_length=100)
    DGEE = models.CharField(max_length=6)

    tutor = models.BooleanField()
    profesor = models.BooleanField()

    fecha_acreditacion = models.DateField()
    acreditacion = models.CharField(max_length=15,
                                    choices=(('doctorado', 'doctorado'),
                                             ('maestría', 'maestría')))
    entidad = models.ForeignKey(Entidad)

    def __unicode__(self):
        return u"%s" % self.user

    class Meta:
        verbose_name_plural = "Académicos"


class Adscripcion(models.Model):
    academico = models.ForeignKey(Academico, on_delete=models.CASCADE)
    institucion = models.ForeignKey(Institucion)
    nombramiento = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100, blank=True)

    numero_trabajador = models.CharField("en caso de trabajar en la UNAM",
                                         max_length=100,
                                         blank=True)
    def __unicode__(self):
        return u"%s %s en %s" % (self.academico,
                                 self.nombramiento,
                                 self.institucion)

    class Meta:
        verbose_name_plural = "Adscripciones"


class Estudiante(models.Model):
    user = models.ForeignKey(User)
    ingreso = models.PositiveSmallIntegerField("año de ingreso al posgrado")
    semestre = models.PositiveSmallIntegerField(
        "semestre de ingreso al posgrado")
    entidad = models.ForeignKey(Entidad)
    convenio = models.CharField(max_length=100, blank=True)
    plan = models.CharField("clave del plan de estudios", max_length=100)
    doctorado_directo = models.BooleanField()
    campo_conocimiento = models.ForeignKey(CampoConocimiento)
    nombre_proyecto = models.CharField(max_length=200)
    estado = models.CharField(max_length=15,
                              choices=(('graduado', 'graduado'),
                                       ('egresado', 'egresado'),
                                       ('vigente', 'vigente'),
                                       ('baja', 'baja'),
                                       ('suspenso', 'suspenso')))
    fecha_baja = models.DateField(blank=True)
    motivo_baja = models.CharField(max_length=200,
                                   blank=True)

    titulacion_licenciatura = models.BooleanField(
        "primer año de maestría para obtener grado de licenciatura")

    fecha_titulacion = models.DateField(blank=True)
    folio_titulacion = models.CharField(max_length=200, blank=True)
    mencion_honorifica = models.BooleanField(blank=True)
    medalla_alfonso_caso = models.BooleanField(blank=True)
    semestre_graduacion = models.PositiveSmallIntegerField(blank=True)

    def __unicode__(self):
        return u"%s en %s" % (self.user, self.plan)


class Beca(models.Model):
    estudiante = models.ForeignKey(Estudiante)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s %s" % (self.estudiante, self.tipo)


class Asunto(models.Model):
    resumen = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100,
                            choices=[('solicitud', 'solicitud'),
                                     ('cambio', 'cambio'),
                                     ('etc', 'etc')])
    solicitante = models.ForeignKey(User)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # sesion del CA
    # archivos anexos
    descripcion = models.TextField()
    acuerdo = models.CharField(max_length=300)
    fecha_resolucion = models.DateTimeField()
    estado = models.CharField(max_length=30)

    def __unicode__(self):
        return u"%s [%s]" % (self.titulo, self.tipo)


class Anexo(models.Model):
    asunto = models.ForeignKey(Asunto)
    archivo = models.FileField()
    fecha = models.DateTimeField(auto_now_add=True)


class Comentario(models.Model):
    asunto = models.ForeignKey(Asunto)
    fecha = models.DateTimeField()
    comentario = models.CharField(max_length=300)
    # anexo?
