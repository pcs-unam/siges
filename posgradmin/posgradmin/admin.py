# coding: utf-8
from django.http import HttpResponseRedirect
from django.contrib import admin

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


from .models import Perfil, Academico, Estudiante, \
    GradoAcademico, Institucion, CampoConocimiento, \
    Solicitud, Proyecto, Dictamen, \
    Comite, Curso, Asignatura, Sesion, Adscripcion, \
    LineaInvestigacion, AnexoExpediente, Acreditacion, \
    ConvocatoriaCurso
    

from .admin_action_academicos import exporta_resumen_academicos

from django.utils.html import format_html


admin.site.site_header = \
                "Administración de Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_title = "Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_url = "/"


class EstudianteAdmin(admin.ModelAdmin):
    search_fields = ['cuenta',
                     'user__first_name',
                     'user__last_name',
                     'user__email', ]
    list_display = ['user', 'cuenta',
                    'plan', 'ingreso', ]

    list_filter = ['plan',
                   'ingreso', ]

    def unificado(self, estudiante):
        return format_html(estudiante.as_a())

    unificado.short_description = 'Vista unificada'


admin.site.register(Estudiante, EstudianteAdmin)


class AcreditacionInline(admin.TabularInline):
    model = Acreditacion
    fk_name = 'academico'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    fields = ['fecha', 'acreditacion', 'comentario', ]


class AcademicoAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

    inlines = [AcreditacionInline, ]

    list_display = ['fullname',
                    'perfil_personal_completo',
                    'resumen_completo',
                    'perfil_comite',
    ]
    list_filter = [
                   'acreditacion',
                   'resumen_completo',
                   'perfil_personal_completo',
                       ]

    readonly_fields = ['fecha_acreditacion',
                       'acreditacion' ]
    
    fieldsets = (
        (None,
         {'fields': ('user',
                     'observaciones',)}),
        ('Participación en el Programa',
         {'fields': ('acreditacion',
                     'fecha_acreditacion',
                     'comite_academico',
                     'estimulo_UNAM',
                     'nivel_SNI',
                     'CVU',
                     'anexo_CV',
                     'anexo_solicitud',
                     'ultimo_grado'
                     )}),
        ('Líneas de investigación, Campos de Conocimiento',
         {'fields': ('lineas_de_investigacion',
                     'campos_de_conocimiento')}),
        ('Formación de EStudiantes',
         {'fields': (
             'tesis_doctorado',
             'tesis_doctorado_5',
             'tesis_maestria',
             'tesis_maestria_5',
             'tesis_licenciatura',
             'tesis_licenciatura_5',
             'tutor_principal_otros_programas',

             'comite_doctorado_otros',
             'comite_maestria_otros',

             'otras_actividades',
             )}),
        ('En el PCS',
         {'fields': (
             'participacion_comite_maestria',
             'participacion_tutor_maestria',
             'participacion_comite_doctorado',
             'participacion_tutor_doctorado',
             )}),
        ('Publicaciones',
         {'fields': (
             'articulos_internacionales_5',
             'articulos_nacionales_5',
             'articulos_internacionales',
             'articulos_nacionales',
             'capitulos',
             'capitulos_5',
             'libros',
             'libros_5',
             'top_5',
             'otras_publicaciones'
         )}),
        ("Actividad profesional y de Investigación",
         {"fields": ("lineas",
                     'palabras_clave',
                     'motivacion',
                     'proyectos_vigentes',)}),
        ("Disponibilidad",
         {"fields": ("disponible_miembro",
                     'disponible_tutor',)}),
    )

    def fullname(self, obj):
        name = obj.user.get_full_name()
        if name:
            return name
        else:
            return obj.user.username

    def perfil_comite(self, academico):
        return format_html(academico.perfil_comite_anchor())

    perfil_comite.short_description = u'Perfil para el Comité Académico'


    actions = ['actualiza_campos',
               exporta_resumen_academicos
    ]

    def actualiza_campos(self, request, queryset):
        for a in queryset:
            a.semaforo_doctorado = a.verifica_semaforo_doctorado()
            a.semaforo_maestria = a.verifica_semaforo_maestria()
            a.verifica_titulo_honorifico()
            a.copia_ultima_acreditacion()
            a.save()

    actualiza_campos.\
        short_description = "actualiza semáforos y otros campos computados"



admin.site.register(Academico, AcademicoAdmin)


class AdscripcionAdmin(admin.ModelAdmin):
    search_fields = ['perfil__user__first_name',
                     'perfil__user__last_name']
    list_display = ['perfil',
                    'institucion',
                    'nombramiento',
                    'anno_nombramiento']
    list_filter = ['catedra_conacyt', 'asociacion_PCS', ]


admin.site.register(Adscripcion, AdscripcionAdmin)


class ComiteAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'tipo', 'miembro1', 'miembro2', 'miembro3']
    search_fields = ['estudiante__user__first_name',
                     'estudiante__user__last_name']


admin.site.register(Comite, ComiteAdmin)


class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ['asignatura', 'clave', 'tipo', 'estado', ]


admin.site.register(Asignatura, AsignaturaAdmin)




def activa_curso(modeladmin, request, queryset):
    for c in queryset.all():
        c.activo = True
        c.save()
        
    return HttpResponseRedirect('/admin/posgradmin/curso')


activa_curso.short_description = "Marcar cursos como activos"


def desactiva_curso(modeladmin, request, queryset):
    for c in queryset.all():
        c.activo = False
        c.save()
        
    return HttpResponseRedirect('/admin/posgradmin/curso')


desactiva_curso.short_description = "Marcar cursos como inactivos"



class CursoAdmin(admin.ModelAdmin):
    list_display = ['asignatura', 'lista_academicos',
                    'year', 'semestre', 'intersemestral', 'sede', 'activo']
    list_filter = ['year',
                   'semestre',
                   'activo',
    ]

    def lista_academicos(self, obj):
        return ", ".join([str(a) for a in obj.academicos.all()])
    
    lista_academicos.short_description = "Académicos"
    
    autocomplete_fields = ['academicos',]
    readonly_fields = ['profesores', 'contacto', ]

    actions = [activa_curso, desactiva_curso]
    
    
admin.site.register(Curso, CursoAdmin)


class GradoAcademicoAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['grado_obtenido', 'nivel', 'user',
                    'institucion', 'fecha_obtencion']


admin.site.register(GradoAcademico, GradoAcademicoAdmin)


class InstitucionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'suborganizacion', 'dependencia_UNAM']


admin.site.register(Institucion, InstitucionAdmin)


class SesionAdmin(admin.ModelAdmin):
    search_fields = ['descripcion', 'fecha']
    list_display = ['fecha', 'descripcion',
                    'unificado']

    def unificado(self, sesion):
        return format_html(sesion.as_a())

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
        return format_html(solicitud.solicitante.perfil)

    unificado.short_description = 'Ver'


admin.site.register(Solicitud, SolicitudAdmin)


class AdscripcionInline(admin.TabularInline):
    model = Adscripcion
    fk_name = 'perfil'
    extra = 1


class PerfilAdmin(admin.ModelAdmin):
    list_display = [
        'fullname',
        'telefono',
        'email',
        'perfil_comite',
       ]
    search_fields = ['user__first_name', 'user__last_name']

    inlines = [AdscripcionInline, ]

    def email(self, obj):
        return obj.user.email

    def fullname(self, obj):
        name = obj.user.get_full_name()
        if name:
            return name
        else:
            return obj.user.username

    def perfil_comite(self, perfil):
        return format_html(perfil.perfil_comite_anchor())

    perfil_comite.short_description = u'Perfil para el Comité Académico'


admin.site.register(Perfil, PerfilAdmin)


class UserProfileInline(admin.StackedInline):
    model = Perfil
    max_num = 1
    can_delete = False


class AnexoExpedienteInline(admin.StackedInline):
    model = AnexoExpediente


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline, AnexoExpedienteInline]
    ordering = ('username', 'first_name', 'last_name', '-date_joined')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(CampoConocimiento)
admin.site.register(LineaInvestigacion)
# admin.site.register(Comentario)
admin.site.register(Proyecto)
admin.site.register(Dictamen)


class AnexoExpedienteAdmin(admin.ModelAdmin):
    def fullname(self, obj):
        name = obj.user.get_full_name()
        if name:
            return name
        else:
            return obj.user.username


    list_display = ['fullname', 'fecha', 'archivo']
    search_fields = ['user__username', 'user__first_name', 'user__last_name',
                     'archivo',
                     'fecha']
    list_filter = ['fecha']


admin.site.register(AnexoExpediente, AnexoExpedienteAdmin)



class AcreditacionAdmin(admin.ModelAdmin):
    list_display = ['acreditacion', 'academico', 'fecha']
    search_fields = ['academico__user__username',
                     'academico__user__first_name',
                     'academico__user__last_name', ]
    list_filter = ['acreditacion', ]

admin.site.register(Acreditacion, AcreditacionAdmin)




class ConvocatoriaCursoAdmin(admin.ModelAdmin):
    list_display = ['year', 'semestre', 'status']
    list_filter = ['status', ]

admin.site.register(ConvocatoriaCurso, ConvocatoriaCursoAdmin)
