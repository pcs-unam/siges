# coding: utf-8

from django.db import models

from django.contrib.auth.models import User

from settings import solicitudes_profesoriles,\
    solicitudes_tutoriles, solicitud_otro,\
    solicitudes_estados


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


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    curp = models.CharField(max_length=100)
    rfc = models.CharField(max_length=100)

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

    def __unicode__(self):
        return u"%s" % self.user

    class Meta:
        verbose_name_plural = "Perfiles"


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

    documento = models.FileField("Copia de documento probatorio")

    def __unicode__(self):
        return u"%s @ %s" % (self.grado_obtenido, self.institucion)

    class Meta:
        verbose_name_plural = "Grados académicos"


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
    DGEE = models.CharField(max_length=6)

    tutor = models.BooleanField(default=False)
    profesor = models.BooleanField(default=False)

    fecha_acreditacion = models.DateField(blank=True, null=True)
    acreditacion = models.CharField(max_length=15,
                                    choices=(('doctorado', 'doctorado'),
                                             ('maestría', 'maestría')))
    entidad = models.ForeignKey(Entidad, null=True, blank=True)

    def solicitudes(self, estado=None):
        if estado is None:
            return Solicitud.objects.filter(solicitante=self.user)
        else:
            return Solicitud.objects.filter(
                solicitante=self.user).filter(
                    estado=estado)

    def cuantas_solicitudes(self):
        solicitudes = [(estado[0], self.solicitudes(estado=estado[0]).count())
                       for estado in solicitudes_estados]
        solicitudes.append(('todas', self.solicitudes().count()))

        return solicitudes

    def __unicode__(self):
        estado = []
        if self.tutor:
            estado.append("tutor acreditado")
        if self.profesor:
            estado.append("profesor")

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ingreso = models.PositiveSmallIntegerField("año de ingreso al posgrado",
                                               blank=True, null=True)
    semestre = models.PositiveSmallIntegerField(
        "semestre de ingreso al posgrado",
        choices=((1, 1),
                 (2, 2)),
        blank=True, null=True)
    entidad = models.ForeignKey(Entidad, null=True, blank=True)
    convenio = models.CharField(max_length=100, blank=True)
    plan = models.CharField("clave del plan de estudios",
                            max_length=100, blank=True)
    doctorado_directo = models.BooleanField(default=False)
    estado = models.CharField(max_length=15,
                              choices=(('aspirante', 'aspirante'),
                                       ('graduado', 'graduado'),
                                       ('egresado', 'egresado'),
                                       ('vigente', 'vigente'),
                                       ('baja', 'baja'),
                                       ('suspenso', 'suspenso')))
    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=200,
                                   blank=True)

    titulacion_licenciatura = models.BooleanField(
        "primer año de maestría para obtener grado de licenciatura",
        default=False)

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
        if estado is None:
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
        return u"%s [%s]" % (self.user, self.estado)

    def comite_tutoral(self):
        pass

    def get_proyecto(self):
        if self.proyecto_set.count() == 0:
            return None

        aprobados = []
        for p in self.proyecto_set.order_by('id'):
            if p.aprobado():
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


class Solicitud(models.Model):
    resumen = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100,
                            choices=solicitudes_profesoriles +
                            solicitudes_tutoriles + solicitud_otro)
    solicitante = models.ForeignKey(User)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # sesion del CA
    descripcion = models.TextField(blank=True)

    estado = models.CharField(max_length=30, default="nueva")

    def dictamen_final(self):
        try:
            return self.dictamen_set.exclude(
                asistente=None).first().resolucion
        except:
            return None

    def __unicode__(self):
        return u"#%s %s [%s]" % (self.id, self.resumen, self.solicitante)

    class Meta:
        verbose_name_plural = "Solicitudes"


class Proyecto(models.Model):
    campo_conocimiento = models.ForeignKey(CampoConocimiento)
    nombre = models.CharField(max_length=200)
    estudiante = models.ForeignKey(Estudiante)
    solicitud = models.ForeignKey(Solicitud)

    def aprobado(self):
        if self.solicitud.dictamen_final() == 'concedida':
            return True
        else:
            return False

    def __unicode__(self):
        if self.aprobado():
            estado = 'aprobado'
        else:
            estado = 'no aprobado'
        return u"%s en %s (%s)" % (self.nombre,
                                   self.campo_conocimiento,
                                   estado)


class Anexo(models.Model):
    solicitud = models.ForeignKey(Solicitud)
    autor = models.ForeignKey(User)
    fecha = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField()

    def __unicode__(self):
        return u"%s anexo a #%s por %s el %s]" % (self.archivo,
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

    def __unicode__(self):
        return "%s (asistente de proceso)" % self.user


class Dictamen(models.Model):
    resolucion = models.CharField(max_length=15,
                                  choices=(('concedida', 'concedida'),
                                           ('denegada', 'denegada')))
    solicitud = models.ForeignKey(Solicitud)
    academico = models.ForeignKey(Academico, null=True, blank=True)
    asistente = models.ForeignKey(Asistente, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Dictámenes"

    def __unicode__(self):
        if self.academico:
            autor = self.academico
        else:
            autor = self.asistente
        return u'#%s %s por %s' \
            % (self.solicitud.id,
               self.resolucion,
               autor)


class Curso(models.Model):
    denominacion = models.CharField(max_length=100)
    clave = models.CharField(max_length=100, blank=True, null=True)
    semestre = models.PositiveSmallIntegerField(
        choices=((1, 1),
                 (2, 2)),
        blank=True, null=True)
    campo_conocimiento = models.ForeignKey(CampoConocimiento)
    dosier = models.FileField()
    profesor = models.ForeignKey(Academico)

    def __unicode__(self):
        return u'curso: "%s" por %s' % (self.denominacion, self.profesor)
