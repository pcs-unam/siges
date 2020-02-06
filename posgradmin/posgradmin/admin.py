# coding: utf-8
from django.contrib import admin

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


from .models import Perfil, Academico, Estudiante, \
    GradoAcademico, Institucion, CampoConocimiento, \
    Solicitud, Proyecto, Dictamen, \
    Comite, Curso, Asignatura, Sesion, Adscripcion, \
    LineaInvestigacion, AnexoExpediente

from .admin_action_academicos import exporta_resumen_academicos

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
                    'plan', 'ingreso', 'perfil_publico', ]

    list_filter = ['plan',
                   'ingreso', ]

    def unificado(self, estudiante):
        return estudiante.as_a()

    def perfil_publico(self, estudiante):
        return estudiante.perfil_publico_anchor()
    perfil_publico.allow_tags = True
    perfil_publico.short_description = u'Perfil Público'

    unificado.allow_tags = True
    unificado.short_description = 'Vista unificada'


admin.site.register(Estudiante, EstudianteAdmin)


class AcademicoAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
    list_display = ['fullname',
                    'acreditacion',
                    'perfil_personal_completo',
                    'resumen_completo',
                    'perfil_publico',
                    'perfil_comite',
    ]
    list_filter = ['acreditacion',
                   'disponible_tutor',
                   'disponible_miembro',
                   'resumen_completo',
                   'perfil_personal_completo',
                       ]

    fieldsets = (
        (None,
         {'fields': ('user',
                     'observaciones',)}),
        ('Participación en el Programa',
         {'fields': ('tutor',
                     'comite_academico',
                     'fecha_acreditacion',
                     'ultima_reacreditacion',
                     'acreditacion',
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

    def perfil_publico(self, academico):
        return academico.perfil_publico_anchor()

    perfil_publico.allow_tags = True
    perfil_publico.short_description = u'Perfil Público'

    def perfil_comite(self, academico):
        return academico.perfil_comite_anchor()

    perfil_comite.allow_tags = True
    perfil_comite.short_description = u'Perfil para el Comité Académico'


    actions = ['actualiza_campos',
               exporta_resumen_academicos
    ]

    def actualiza_campos(self, request, queryset):
        for a in queryset:
            a.semaforo_doctorado = a.verifica_semaforo_doctorado()
            a.semaforo_maestria = a.verifica_semaforo_maestria()
            a.verifica_titulo_honorifico()
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


class CursoAdmin(admin.ModelAdmin):
    list_display = ['asignatura', 'profesores',
                    'year', 'semestre', 'intersemestral', 'sede', 'activo']


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


class AdscripcionInline(admin.TabularInline):
    model = Adscripcion
    fk_name = 'perfil'
    extra = 1


class PerfilAdmin(admin.ModelAdmin):
    list_display = [
        'fullname',
        'telefono',
        'email',
        'perfil_publico',
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

    def perfil_publico(self, perfil):
        return perfil.perfil_publico_anchor()

    perfil_publico.allow_tags = True
    perfil_publico.short_description = u'Perfil Público'

    def perfil_comite(self, perfil):
        return perfil.perfil_comite_anchor()

    perfil_comite.allow_tags = True
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
