# coding: utf-8
from django.contrib import admin
from .models import Perfil, Academico, Estudiante, \
    GradoAcademico, Institucion, Entidad, CampoConocimiento, \
    Solicitud, Proyecto, Dictamen, \
    Comite, Asistente, Curso, Catedra, Sesion, Empleo

admin.site.site_header = \
                "Administración de Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_title = "Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_url = "/"


class EstudianteAdmin(admin.ModelAdmin):
    search_fields = ['cuenta', 'user__first_name', 'user__last_name']
    list_display = ['user', 'cuenta', 'entidad',
                    'plan', 'ingreso', 'unificado']

    def unificado(self, estudiante):
        return estudiante.as_a()

    unificado.allow_tags = True
    unificado.short_description = 'Vista unificada'


admin.site.register(Estudiante, EstudianteAdmin)


class AcademicoAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name']
    list_display = ['nombre_completo', 'titulo',
                    'entidad', 'tutor', 'comite_academico',
                    'nivel_SNI', 'nivel_pride',
                    'unificado']

    def unificado(self, academico):
        return academico.as_a()

    unificado.allow_tags = True
    unificado.short_description = 'Vista unificada'


admin.site.register(Academico, AcademicoAdmin)


class EmpleoAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['cargo', 'institucion', 'user']


admin.site.register(Empleo, EmpleoAdmin)


class ComiteAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'tipo', 'presidente', 'secretario', 'vocal']
    search_fields = ['estudiante__user__first_name',
                     'estudiante__user__last_name']


admin.site.register(Comite, ComiteAdmin)


class CursoAdmin(admin.ModelAdmin):
    list_display = ['clave', 'asignatura',
                    'tipo', 'creditos', 'horas_semestre']


admin.site.register(Curso, CursoAdmin)


class CatedraAdmin(admin.ModelAdmin):
    list_display = ['curso', 'profesor', 'semestre', 'year']


admin.site.register(Catedra, CatedraAdmin)


class GradoAcademicoAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['grado_obtenido', 'nivel', 'user',
                    'institucion', 'facultad', 'fecha_obtencion']


admin.site.register(GradoAcademico, GradoAcademicoAdmin)


class InstitucionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'suborganizacion', 'dependencia_unam']


admin.site.register(Institucion, InstitucionAdmin)


class SesionAdmin(admin.ModelAdmin):
    search_fields = ['descripcion', 'fecha']
    list_display = ['fecha', 'descripcion',
                    'unificado']

    def unificado(self, sesion):
        return sesion.as_a()

    unificado.allow_tags = True
    unificado.short_description = 'Ver'


admin.site.register(Sesion, SesionAdmin)


class SolicitudAdmin(admin.ModelAdmin):
    search_fields = ['resumen', 'fecha_creacion',
                     'solicitante__first_name',
                     'solicitante__last_name']
    list_display = ['resumen', 'user', 'fecha_creacion',
                    'unificado', 'estado', 'tipo']

    def unificado(self, solicitud):
        return solicitud.as_a()

    def user(self, solicitud):
        return solicitud.solicitante.perfil

    unificado.allow_tags = True
    unificado.short_description = 'Ver'


admin.site.register(Solicitud, SolicitudAdmin)


admin.site.register(Perfil)
admin.site.register(Entidad)
admin.site.register(CampoConocimiento)
# admin.site.register(Comentario)
admin.site.register(Proyecto)
admin.site.register(Dictamen)
admin.site.register(Asistente)
