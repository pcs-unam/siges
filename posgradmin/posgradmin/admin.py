# coding: utf-8
from django.contrib import admin
from .models import Perfil, Academico, Estudiante, Adscripcion,\
    GradoAcademico, Institucion, Entidad, CampoConocimiento, \
    Solicitud, Comentario, Anexo, Proyecto, Dictamen, \
    Comite, Asistente, Curso, Catedra, Sesion

admin.site.site_header = "Administración de Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_title = "Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_url = "/"


class EstudianteAdmin(admin.ModelAdmin):
    search_fields = ['cuenta', 'user__first_name', 'user__last_name']
    list_display = ['user', 'cuenta', 'entidad', 'plan', 'ingreso']


admin.site.register(Estudiante, EstudianteAdmin)


class AcademicoAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']
    list_display = ['nombre_completo',
                    'entidad', 'tutor', 'nivel_SNI', 'nivel_pride']


admin.site.register(Academico, AcademicoAdmin)


class AdscripcionAdmin(admin.ModelAdmin):
    list_display = ['academico', 'institucion', 'nombramiento']


admin.site.register(Adscripcion, AdscripcionAdmin)


class ComiteAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'tipo', 'presidente', 'secretario', 'vocal']
    search_fields = ['estudiante__user__first_name',
                     'estudiante__user__last_name']


admin.site.register(Comite, ComiteAdmin)

admin.site.register(Perfil)
admin.site.register(GradoAcademico)
admin.site.register(Institucion)
admin.site.register(Entidad)
admin.site.register(CampoConocimiento)
admin.site.register(Solicitud)
admin.site.register(Comentario)
admin.site.register(Proyecto)
admin.site.register(Dictamen)
admin.site.register(Asistente)
admin.site.register(Curso)
admin.site.register(Catedra)
admin.site.register(Sesion)
