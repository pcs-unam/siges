from django.db import models

from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    nacionalidad  = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)
    telefono_movil = models.CharField(max_length=100)
    CURP = models.CharField(max_length=100)
    RFC = models.CharField(max_length=100)
    email1 = models.CharField(max_length=100)
    email2 = models.CharField(max_length=100)
    website = models.CharField(max_length=100)

    genero = models.CharField(max_length=1, choices=(('M', 'masculino'),
                                                     ('F', 'femenino'),
                                                     ('N', 'no especificado'))
    
    pub_date = models.DateTimeField('date published')
