# coding: utf-8
import os
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

from settings import solicitudes_profesoriles,\
    solicitudes_tutoriles, solicitud_otro,\
    solicitudes_estados, MEDIA_ROOT, MEDIA_URL
    
from pprint import pprint


class Institucion(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s, %s, %s" % (self.nombre, self.estado, self.pais)

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


def headshot_path(instance, filename):
    extension = filename.split('.')[-1]
    return 'media/headshots/%s.%s' % (instance.user.id, extension)


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    curp = models.CharField(max_length=100, blank=True)
    rfc = models.CharField(max_length=100, blank=True)

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

    fecha_nacimiento = models.DateField('fecha de nacimiento')

    headshot = models.ImageField(upload_to=headshot_path,
                                 blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.user

    class Meta:
        verbose_name_plural = "Perfiles"


def grado_path(instance, filename):
    return os.path.join(MEDIA_ROOT,
                        'grados/%s/%s' % (instance.user.id,
                                          filename))


class GradoAcademico(models.Model):
    user = models.ForeignKey(User)

    nivel = models.CharField(max_length=15,
                             choices=(('licenciatura', 'licenciatura'),
                                      ('maestria', 'maestria'),
                                      ('doctorado', 'doctorado')))

    grado_obtenido = models.CharField(max_length=100)

    institucion = models.ForeignKey(Institucion)
    facultad = models.CharField(max_length=100)

    fecha_obtencion = models.DateField("Fecha de obtención de grado")
    promedio = models.DecimalField(max_digits=4, decimal_places=2)

    documento = models.FileField("Copia de documento probatorio",
                                 upload_to=grado_path)

    def documento_url(self):
        return "%s/grados/%s/%s" % (MEDIA_URL,
                                    self.user.id,
                                    os.path.basename(self.documento.path))

    def __unicode__(self):
        return u"%s @ %s" % (self.grado_obtenido, self.institucion)

    class Meta:
        verbose_name_plural = "Grados académicos"


class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cuenta = models.CharField(max_length=100)
    ingreso = models.PositiveSmallIntegerField("año de ingreso al posgrado",
                                               blank=True, null=True)
    semestre = models.PositiveSmallIntegerField(
        "semestre de ingreso al posgrado",
        choices=((1, 1),
                 (2, 2)),
        blank=True, null=True)
    entidad = models.ForeignKey(Entidad, null=True, blank=True)
    convenio = models.CharField(max_length=100, blank=True)
    # plan = models.CharField("clave del plan de estudios",
    #                         max_length=100, blank=True)

    plan = models.CharField(
        max_length=20,
        choices=((1, u"maestría"),
                 (2, u"doctorado"),
                 (3, u"doctorado directo"),
                 (4, u"opción a titulación")))

    estado = models.CharField(max_length=15,
                              default=u"vigente",
                              choices=((u"graduado", u"graduado"),
                                       (u"egresado", u"egresado"),
                                       (u"vigente", u"vigente"),
                                       (u"baja", u"baja"),
                                       (u"suspenso", u"suspenso")))

    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=200,
                                   blank=True)

    fecha_titulacion = models.DateField(blank=True, null=True)
    folio_titulacion = models.CharField(max_length=200, blank=True)
    mencion_honorifica = models.BooleanField(default=False)
    medalla_alfonso_caso = models.BooleanField(default=False)
    semestre_graduacion = models.PositiveSmallIntegerField(blank=True,
                                                           null=True)

    def faltan_documentos(self):
        if self.user.gradoacademico_set.count() == 0:
            return True
        else:
            return False

    def solicitudes(self, estado=None):
        if estado is None or estado is 'todas':
            return Solicitud.objects.filter(
                solicitante=self.user
            )
        else:
            return Solicitud.objects.filter(
                solicitante=self.user).filter(
                    estado=estado)

    def cuantas_solicitudes(self):
        solicitudes = [(estado[0], self.solicitudes(estado=estado[0]).count())
                       for estado in solicitudes_estados]
        solicitudes.append(('todas',
                            self.solicitudes().count()))

        return solicitudes

    def __unicode__(self):
        return u"%s [%s] %s" % (self.user, self.estado, self.user.get_full_name())

    def comite_tutoral(self):
        for c in Comite.objects.filter(Q(tipo='tutoral') & Q(estudiante=self)):
            if c.solicitud.dictamen_final():
                if c.solicitud.dictamen_final().resolucion == 'concedida':
                    return c
        return None
            

    def get_proyecto(self):
        if self.proyecto_set.count() == 0:
            return None

        aprobados = []
        for p in self.proyecto_set.order_by('id'):
            if p.aprobado:
                aprobados.append(p)

        if aprobados:
            return aprobados[-1]
        else:
            return self.proyecto_set.last()

    def get_proyecto_no_aprobado(self):
        for p in self.proyecto_set.order_by('-id'):
            if p.id > self.get_proyecto().id \
               and p.solicitud.dictamen_final() is None:
                return p
        return None


class Beca(models.Model):
    estudiante = models.ForeignKey(Estudiante)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s %s" % (self.estudiante, self.tipo)


class Sesion(models.Model):
    fecha = models.DateField()
    descripcion = models.CharField(max_length=100,
                                   default="sesión ordinaria")
    
    def __unicode__(self):
        return u'%s, %s' % (self.fecha,
                            self.descripcion)

    class Meta:
        verbose_name_plural = "Sesiones"

    
class Solicitud(models.Model):
    resumen = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100,
                            choices=solicitudes_profesoriles +
                            solicitudes_tutoriles + solicitud_otro)
    solicitante = models.ForeignKey(User)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    sesion = models.ForeignKey(Sesion, blank=True, null=True)    
    descripcion = models.TextField(blank=True)

    estado = models.CharField(max_length=30, default="nueva",
                              choices=solicitudes_estados)

    def agendable(self, user):
        if hasattr(user, 'asistente') or user.is_staff:
            if self.estado == 'nueva':
                return True
    
    def dictaminable(self, user):

        if self.estado == 'agendada':

            if self.solicitante.id == user.id:
                return False

            if hasattr(user, 'asistente') or user.is_staff \
               or user.academico.acreditado():
                return True
        else:
            return False

    def cancelable(self, user):
        if self.estado == 'nueva':  # sólo nuevas se cancelan
            if self.predictamen():
                return False

            if self.solicitante.id == user.id:   # cancelar las propias
                return True
        else:
            return False

    def dictamen_final(self):
        for d in self.dictamen_set.all():
            if d.autor.is_staff or hasattr(d.autor, 'asistente'):
                return d
        return None

    def predictamen(self):
        if self.dictamen_final():
            return True
        elif self.dictamen_set.count() > 0:
            return True
        else:
            return False

    def __unicode__(self):
        return u"#%s %s [%s]" % (self.id, self.resumen, self.solicitante)

    def as_a(self):
        icon = """<span class='glyphicon glyphicon-{icon}'
                        aria-hidden=true></span>"""
        if self.dictamen_final():
            if self.dictamen_final().resolucion == 'concedida':
                status = '%s' % icon.format(icon='thumbs-up')
            else:
                status = '%s' % icon.format(icon='thumbs-down')
        elif self.predictamen():
            status = '%s' % icon.format(icon='eye-open')
        elif self.estado == 'cancelada':
            return u"""<a href='/inicio/solicitudes/%s'>
                       <strike>#%s</strike></a>""" % (
                self.id, self.id)
        elif self.estado == 'agendada':
            status = '%s' % icon.format(icon='calendar')
        else:
            status = self.estado

        return u"""<a href='/inicio/solicitudes/%s'>#%s %s</a>""" % (
            self.id, self.id, status)

    class Meta:
        verbose_name_plural = "Solicitudes"


class Proyecto(models.Model):
    campo_conocimiento = models.ForeignKey(CampoConocimiento)
    nombre = models.CharField(max_length=200)
    estudiante = models.ForeignKey(Estudiante)
    solicitud = models.ForeignKey(Solicitud, blank=True, null=True)
    aprobado = models.BooleanField(default=False)

    def update_status(self):
        if self.solicitud.dictamen_final():
            if self.solicitud.dictamen_final().resolucion == 'concedida':
                self.aprobado = True
                self.save()

    def __unicode__(self):
        if self.aprobado:
            estado = 'aprobado'
        else:
            estado = 'no aprobado'
        return u"%s en %s (%s)" % (self.nombre,
                                   self.campo_conocimiento,
                                   estado)


def anexo_path(instance, filename):
    return os.path.join(MEDIA_ROOT,
                        'solicitudes/%s/%s' % (instance.solicitud.id,
                                               filename))


class Anexo(models.Model):
    solicitud = models.ForeignKey(Solicitud)
    autor = models.ForeignKey(User)
    fecha = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to=anexo_path)

    def url(self):
        return "%s/solicitudes/%s/%s" % (MEDIA_URL,
                                         self.solicitud.id,
                                         os.path.basename(self.archivo.path))

    def basename(self):
        return os.path.basename(self.archivo.file.name)

    def __unicode__(self):
        return u"[%s anexo a #%s por %s el %s]" % (self.basename(),
                                                   self.solicitud.id,
                                                   self.autor,
                                                   self.fecha)


class Acuerdo(models.Model):
    solicitud = models.ForeignKey(Solicitud)
    archivo = models.FileField()
    fecha = models.DateTimeField(auto_now_add=True)
    # id asamblea


class Comentario(models.Model):
    solicitud = models.ForeignKey(Solicitud)
    autor = models.ForeignKey(User)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.CharField(max_length=300)
    # anexo?

    def __unicode__(self):
        return u'%s por %s: "%s"' % (self.fecha, self.autor, self.comentario)


class Academico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nivel_pride = models.CharField(max_length=15, choices=(('A', 'A'),
                                                           ('B', 'B'),
                                                           ('C', 'C')))
    nivel_SNI = models.CharField(max_length=15,
                                 choices=(('sin SNI', 'sin SNI'),
                                          ('I', 'I'),
                                          ('II', 'II'),
                                          ('III', 'III'),
                                          ('C', 'C'),
                                          ('E', 'E')))
    CVU = models.CharField(max_length=100)
    DGEE = models.CharField(max_length=6, blank=True, null=True)

    tutor = models.BooleanField(default=False)
    comite_academico = models.BooleanField(default=False)

    fecha_acreditacion = models.DateField(blank=True, null=True)
    acreditacion = models.CharField(max_length=15,
                                    choices=(('doctorado', 'doctorado'),
                                             ('maestría', 'maestría')))
    entidad = models.ForeignKey(Entidad, null=True, blank=True)

    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE)

    def acreditado(self):
        if self.solicitud.dictamen_final() is None:
            return False
        elif self.solicitud.dictamen_final().resolucion == 'concedida':
            self.fecha_acreditacion = self.solicitud.dictamen_final().fecha
            self.tutor = True
            self.save()
            return True

    def solicitudes(self, estado=None):
        solicitudes_de_estudiantes = set()
        for e in self.estudiantes():
            for s in e.solicitudes():
                solicitudes_de_estudiantes.add(s.id)

        if estado is None or estado == 'todas':
            return Solicitud.objects.filter(
                Q(pk__in=solicitudes_de_estudiantes)
                | Q(solicitante=self.user))
        else:
            return Solicitud.objects.filter(
                (Q(pk__in=solicitudes_de_estudiantes)
                 | Q(solicitante=self.user))
                & Q(estado=estado))

    def cuantas_solicitudes(self):
        solicitudes = [(estado[0], self.solicitudes(estado=estado[0]).count())
                       for estado in solicitudes_estados]
        solicitudes.append(('todas', self.solicitudes().count()))

        return solicitudes

    def estudiantes(self):
        estudiantes = set()
        if self.tutor:
            for c in Comite.objects.filter(Q(tipo='tutoral')
                                           & (Q(presidente=self)
                                              | Q(secretario=self)
                                              | Q(vocal=self))):
                if c.solicitud.dictamen_final():
                    if c.solicitud.dictamen_final().resolucion == 'concedida':
                        estudiantes.add(c.estudiante)
                elif c.solicitud.estado != 'cancelada':
                    estudiantes.add(c.estudiante)
            return estudiantes
        else:
            return []

    def comites(self):
        comites = list()

        for c in Comite.objects.filter(Q(tipo='candidatura')|Q(tipo='grado')
                                       & (Q(presidente=self)
                                          | Q(secretario=self)
                                          | Q(vocal=self))):
            if c.solicitud.dictamen_final():
                if c.solicitud.dictamen_final().resolucion == 'concedida':
                    comites.append(c)
        return comites

        
    def __unicode__(self):
        estado = []
        if self.tutor:
            estado.append("tutor acreditado")

        return u"%s %s (%s), %s" % (self.user.first_name,
                                    self.user.last_name,
                                    self.user.username,
                                    ", ".join(estado))

    class Meta:
        verbose_name_plural = "Académicos"


class Adscripcion(models.Model):
    academico = models.ForeignKey(Academico, on_delete=models.CASCADE)
    institucion = models.ForeignKey(Institucion)
    nombramiento = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100, blank=True)

    numero_trabajador = models.CharField("Número de trabajador (UNAM)",
                                         max_length=100,
                                         blank=True, null=True)

    def __unicode__(self):
        return u"%s %s en %s" % (self.academico,
                                 self.nombramiento,
                                 self.institucion)

    class Meta:
        verbose_name_plural = "Adscripciones"


class Comite(models.Model):
    presidente = models.ForeignKey(Academico,
                                   related_name="preside_comites")
    secretario = models.ForeignKey(Academico,
                                   related_name="secretario_comites")
    vocal = models.ForeignKey(Academico,
                              related_name="vocal_comites")
    solicitud = models.ForeignKey(Solicitud)
    estudiante = models.ForeignKey(Estudiante)
    tipo = models.CharField(max_length=15,
                            choices=(('tutoral', 'tutoral'),
                                     ('candidatura', 'candidatura'),
                                     ('grado', 'grado')))
    class Meta:
        verbose_name_plural = "Comités"
    

    def __unicode__(self):
        return u'presidente: %s, secretario: %s, vocal: %s' \
            % (self.presidente,
               self.secretario,
               self.vocal)

    def as_ul(self):
        ul = """<ul>
                 <li><strong>presidente:</strong> %s</li>
                 <li><strong>secretario:</strong> %s</li>
                 <li><strong>vocal:</strong> %s</li>
                </ul>"""
        return ul % (self.presidente,
                     self.secretario,
                     self.vocal)


class Asistente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def cuantas_solicitudes(self):
        solicitudes = [(estado[0], self.solicitudes(estado=estado[0]).count())
                       for estado in solicitudes_estados]
        solicitudes.append(('todas', self.solicitudes().count()))

        return solicitudes

    def solicitudes(self, estado=None):
        if estado is None or estado is 'todas':
            return Solicitud.objects.all()
        else:
            return Solicitud.objects.filter(estado=estado)

    class Meta:
        verbose_name_plural = "Asistentes de Proceso"

        
    def __unicode__(self):
        return "%s (asistente de proceso)" % self.user


class Dictamen(models.Model):
    resolucion = models.CharField(max_length=15,
                                  choices=(('concedida', 'concedida'),
                                           ('denegada', 'denegada')))
    solicitud = models.ForeignKey(Solicitud)
    autor = models.ForeignKey(User, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Dictámenes"

    def __unicode__(self):
        return u'#%s %s por %s' \
            % (self.solicitud.id,
               self.resolucion,
               self.autor)


def curso_path(instance, filename):
    return os.path.join(MEDIA_ROOT,
                        'cursos/%s/%s' % (instance.id,
                                          filename))


class Curso(models.Model):
    asignatura = models.CharField(max_length=100)
    clave = models.CharField(max_length=100, blank=True, null=True)
    programa = models.FileField("Documento con descripción extensa.",
                                upload_to=curso_path)

    def programa_url(self):
        return "%s/cursos/%s/%s" % (MEDIA_URL,
                                    self.id,
                                    os.path.basename(self.programa.path))

    def __unicode__(self):
        return u'%s: %s' % (self.clave,
                                 self.asignatura)


class Catedra(models.Model):
    curso = models.ForeignKey(Curso)
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE)
    semestre = models.PositiveSmallIntegerField(
        choices=((1, 1), (2, 2)))
    year = models.PositiveSmallIntegerField()
    profesor = models.ForeignKey(Academico, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Cátedras"

    def __unicode__(self):
        return u'%s, %s %s, por %s' % (self.curso,
                                       self.semestre,
                                       self.year,
                                       self.profesor)

        
class Acta(models.Model):
    acuerdos = models.TextField(blank=True)
    sesion = models.ForeignKey(Sesion)

    
