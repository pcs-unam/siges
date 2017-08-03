# coding: utf-8
from django.contrib import admin
from .models import Perfil, Academico, Estudiante, Adscripcion,\
    GradoAcademico, Institucion, Entidad, CampoConocimiento, \
    Beca, Solicitud, Comentario, Anexo, Proyecto, Dictamen, \
    Comite, Asistente, Curso, Catedra

admin.site.site_header = "Administración de Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_title = "Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_url = "/"


admin.site.register(Perfil)
admin.site.register(Academico)
admin.site.register(Estudiante)
admin.site.register(Adscripcion)
admin.site.register(GradoAcademico)
admin.site.register(Institucion)
admin.site.register(Entidad)
admin.site.register(CampoConocimiento)
# admin.site.register(Beca)
admin.site.register(Solicitud)
admin.site.register(Comentario)
admin.site.register(Anexo)
admin.site.register(Proyecto)
admin.site.register(Dictamen)
admin.site.register(Comite)
admin.site.register(Asistente)
admin.site.register(Curso)
admin.site.register(Catedra)
