# coding: utf-8

from django.db import models

from django.contrib.auth.models import User


class Institucion(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15, choices=(('UNAM', 'UNAM'),
                                                    ('Sector Salud', 'Sector Salud'),
                                                    ('Hospitales', 'Hospitales'),
                                                    ('Gobierno', 'Gobierno'),
                                                    ('Otro', 'otro')))



class Entidad(models.Model):
    nombre = models.CharField(max_length=100)    


class CampoConocimiento(models.Model):
    nombre = models.CharField(max_length=100)    

    
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    CURP = models.CharField(max_length=100)
    RFC = models.CharField(max_length=100)

    telefono = models.CharField(max_length=100)
    telefono_movil = models.CharField(max_length=100)

    direccion1 = models.CharField("direccion linea 1", max_length=150)
    direccion2 = models.CharField("direccion linea 2", max_length=150)
    codigo_postal = models.PositiveSmallIntegerField()
    email1 = models.EmailField(max_length=200)
    email2 = models.EmailField(max_length=200)
    website = models.CharField(max_length=200)

    genero = models.CharField(max_length=1, choices=(('M', 'masculino'),
                                                     ('F', 'femenino'),
                                                     ('N', 'no especificado')))

    nacionalidad  = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField('date published')




class GradoAcademico(models.Model):
    user = models.ForeignKey(User)

    grado = models.CharField(max_length=15, choices=(('licenciatura', 'licenciatura'),
                                                     ('maestria', 'maestria'),
                                                     ('doctorado', 'doctorado')))

    institucion = models.ForeignKey(Institucion)
    facultad = models.CharField(max_length=100)

    fecha_titulacion = models.DateField()
    promedio = models.DecimalField(max_digits=4, decimal_places=2)






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
    acreditacion = models.CharField(max_length=15, choices=(('doctorado', 'doctorado'),
                                                         ('maestría', 'maestría')))





class Adscripcion(models.Model):
    academico = models.ForeignKey(Academico, on_delete=models.CASCADE)
    institucion = models.ForeignKey(Institucion)
    nombramiento = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)

    numero_trabajador = models.CharField("en caso de trabajar en la UNAM", max_length=100)




class Estudiante(models.Model):
    ingreso = models.PositiveSmallIntegerField("año de ingreso al posgrado")
    semestre = models.PositiveSmallIntegerField("semestre de ingreso al posgrado")
    entidad = models.ForeignKey(Entidad)
    convenio = models.CharField(max_length=100)
    plan = models.CharField("clave del plan de estudios", max_length=100)
    doctorado_directo = models.BooleanField()
    campo_conocimiento = models.ForeignKey(CampoConocimiento)
    nombre_proyecto = models.CharField(max_length=200)
    estado = models.CharField(max_length=15, choices=(('graduado', 'graduado'),
                                                      ('egresado', 'egresado'),
                                                      ('vigente', 'vigente'),
                                                      ('baja', 'baja'),
                                                      ('suspenso', 'suspenso')))
    fecha_baja = models.DateField()
    motivo_baja = models.CharField(max_length=200)

    titulacion_licenciatura = models.BooleanField("primer año de maestría para obtener grado de licenciatura")

    fecha_titulacion = models.DateField()
    folio_titulacion = models.CharField(max_length=200)
    mencion_honorifica = models.BooleanField()
    medalla_alfonso_caso = models.BooleanField()
    semestre_graduacion = models.PositiveSmallIntegerField()


class Beca(models.Model):
    estudiante = models.ForeignKey(Estudiante)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=100)
