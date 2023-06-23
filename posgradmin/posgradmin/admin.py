# coding: utf-8
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import admin
from reversion.admin import VersionAdmin


from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline


from .models import Perfil, Academico, Estudiante, \
    GradoAcademico, Institucion, CampoConocimiento, \
    Proyecto, Invitado, InvitadoMembresiaComite, \
    Curso, Asignatura, Sesion, Adscripcion, \
    LineaInvestigacion, AnexoExpediente, Acreditacion, \
    ConvocatoriaCurso, Historial, MembresiaComite, Nota, \
    ApoyoMovilidad, Graduado, Sede, MiembroJuradoGraduacion, InvitadoJuradoGraduacion


from .admin_action_academicos import exporta_resumen_academicos, exporta_emails_cursos, exporta_emails_estudiantes

from django.utils.html import format_html
from django.utils import timezone
from django.utils.text import Truncator


admin.site.site_header = \
                "Administración de Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_title = "Posgrado en Ciencias de la Sostenibilidad"
admin.site.site_url = "/"


class AutoAutor(object):
    exclude = ('autor', )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.autor = request.user
            instance.save()
        formset.save_m2m()



class NotaInline(GenericStackedInline):
    model = Nota
    extra = 0
    fields = ['asunto', 'nota', 'estado', 'archivo' ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'autor', None) is None:
            obj.autor = request.user
        obj.save()


@admin.register(Nota)
class NotaAdmin(VersionAdmin):
    list_filter = ['estado', 'fecha',]
    list_display = ['link_to', 'tipo', 'fecha', 'autor', 'estado', 'objeto',]
    search_fields = ['fecha', 'asunto']
    readonly_fields = ['autor', 'fecha', ]
    exclude = ['content_type', 'object_id']

    def has_add_permission(self, request, obj=None):
        return False

    def tipo(self, obj):
        return obj.content_type.name

    def objeto(self, obj):
        return obj.content_type.get_object_for_this_type(pk=obj.object_id)

    def link_to(self, obj):
        fecha = timezone.localtime(obj.fecha)

        path = reverse('admin:posgradmin_%s_change' % obj.content_type.model.lower(),
                       args=(obj.object_id,))
        change_url = "<a href='%s'>%s</a>" % (path,
                                              obj.asunto)
        return format_html(change_url)

    link_to.allow_tags = True
    link_to.short_description = 'Asunto'


@admin.register(MembresiaComite)
class MembresiaComiteAdmin(VersionAdmin):
    model = MembresiaComite
    list_display = ['estudiante', 'tutor', 'tipo', 'year', 'semestre']

    search_fields = ['estudiante__cuenta',
                     'estudiante__user__first_name',
                     'estudiante__user__last_name',
                     'estudiante__user__email',
                     'tutor__user__first_name',
                     'tutor__user__last_name',
                     'tutor__user__email',]
    list_filter = ['tipo',
                   'year',
                   'semestre' ]

    autocomplete_fields = ['estudiante', 'tutor', ]


@admin.register(ApoyoMovilidad)
class ApoyoMovilidadAdmin(AutoAutor, VersionAdmin):
    search_fields = ['estudiante__cuenta',
                     'estudiante__user__first_name',
                     'estudiante__user__last_name',
                     'estudiante__user__email',
                     'nombre']

    list_display = ['fecha_solicitud',
                    'estudiante',
                    'tipo_apoyo',
                    'tipo_actividad',
                    'nombre',
                    'institucion',
                    'fecha_inicio',
                    'fecha_fin']

    list_filter = ['tipo_apoyo',
                   'tipo_actividad',
                   'estado',]

    inlines = [NotaInline, ]

    autocomplete_fields = ['estudiante', 'institucion',]



class InvitadosJuradoInline(admin.TabularInline):
    model = InvitadoJuradoGraduacion
    fk_name = 'graduado'
    extra = 0
    autocomplete_fields = ['invitado', ]


class MiembrosJuradoInline(admin.TabularInline):
    model = MiembroJuradoGraduacion
    fk_name = 'graduado'
    extra = 0
    autocomplete_fields = ['academico', ]
    
class GraduadoAdmin(AutoAutor, VersionAdmin):
    autocomplete_fields = ['estudiante', ]
    search_fields = ['estudiante__cuenta',
                     'estudiante__user__first_name',
                     'estudiante__user__last_name',
                     'estudiante__user__email']

    list_display = ['fecha',
                    'estudiante',
                    'plan',
                    'year',
                    'semestre',
                    'modalidad_graduacion']

    list_filter = ['year',
                   'semestre',
                   'plan',
                   'modalidad_graduacion']
    inlines = [InvitadosJuradoInline,
               MiembrosJuradoInline,
               NotaInline, ]
    ordering = ("-fecha", "-year", "-semestre")

admin.site.register(Graduado, GraduadoAdmin)

@admin.register(Historial)
class HistorialAdmin(AutoAutor, VersionAdmin):
    search_fields = ['estudiante__cuenta',
                     'estudiante__user__first_name',
                     'estudiante__user__last_name',
                     'estudiante__user__email']
    readonly_fields = ['estudiante']
    list_display = ['fecha',
                    'estudiante',
                    'plan',
                    'year',
                    'semestre',
                    'estado',
                    'institucion']

    list_filter = ['year',
                   'semestre',
                   'institucion',
                   'plan',
                   'permiso_trabajar',
                   'estado']
    inlines = [NotaInline, ]
    autocomplete_fields = ['estudiante',]
    ordering = ("-fecha", "-year", "-semestre")

class SedeInline(admin.TabularInline):
    model = Sede
    fk_name = 'estudiante'
    extra = 0
    show_change_link = True
    classes = ('grp-collapse grp-closed',)
    fields = ['plan', 'sede']


class HistorialInline(admin.TabularInline):
    model = Historial
    fk_name = 'estudiante'
    extra = 0
    show_change_link = True
    classes = ('grp-collapse grp-closed',)

    fields = ['fecha', 'estado', 'plan', 'year', 'semestre', 'institucion']

    readonly_fields = ['institucion',]

    
class TutoresInline(admin.TabularInline):
    model = MembresiaComite
    fk_name = 'estudiante'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    fields = ['year', 'semestre', 'tutor', 'tipo', ]
    autocomplete_fields = ['tutor', ]


class TutoresInvitadosInline(admin.TabularInline):
    model = InvitadoMembresiaComite
    fk_name = 'estudiante'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    fields = ['year', 'semestre', 'invitado', 'tipo', ]
    autocomplete_fields = ['invitado', ]

    
class ProyectosInline(admin.TabularInline):
    model = Proyecto
    fk_name = 'estudiante'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    fields = ['fecha', 'plan', 'titulo', ]


@admin.register(Invitado)
class InvitadoAdmin(AutoAutor, VersionAdmin):
    search_fields = ['nombre', 'correo']
    list_display = ['nombre', 'correo']



@admin.register(Estudiante)
class EstudianteAdmin(AutoAutor, VersionAdmin):
    actions = [exporta_emails_estudiantes, ]
    search_fields = ['cuenta',
                     'user__first_name',
                     'user__last_name',
                     'user__email', ]
    readonly_fields = ['fullname', 'estado', 'plan']
    list_filter = ['estado', 'plan']
    list_display = ['fullname', 'ficha', 'plan', 'estado']

    inlines = [HistorialInline, SedeInline, TutoresInline, TutoresInvitadosInline, ProyectosInline, NotaInline]

    def fullname(self, obj):
        name = obj.user.get_full_name()
        if name:
            return name
        else:
            return obj.user.username


    def ficha(self, estudiante):
        return format_html(estudiante.ficha_a())

    ficha.short_description = u'Ficha resumen de estudiante'


class AcreditacionInline(admin.TabularInline):
    model = Acreditacion
    fk_name = 'academico'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    fields = ['fecha', 'acreditacion', 'comentario', ]


class AcademicoAdmin(AutoAutor, VersionAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

    inlines = [AcreditacionInline, NotaInline]

    def perfil_profesor(self, obj):
        return obj.perfil_profesor_completo
    perfil_profesor.boolean = True
    
    list_display = ['fullname',
                    'acreditacion',
                    'perfil_personal_completo',
                    'perfil_profesor',
                    'resumen_completo',
                    'perfil_comite',
    ]
    list_filter = [
                   'acreditacion',
                   'resumen_completo',
                   'perfil_personal_completo',
                       ]

    readonly_fields = ['fecha_acreditacion',
                       'acreditacion',
                       'CVU' ]

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


class AdscripcionAdmin(VersionAdmin):
    search_fields = ['perfil__user__first_name',
                     'perfil__user__last_name']
    list_display = ['perfil',
                    'institucion',
                    'nombramiento',
                    'anno_nombramiento']
    list_filter = ['catedra_conacyt', 'asociacion_PCS', ]


admin.site.register(Adscripcion, AdscripcionAdmin)

@admin.register(Asignatura)
class AsignaturaAdmin(VersionAdmin):
    search_fields = ['asignatura',
                     'clave',
                     'proponente__first_name',
                     'proponente__last_name']
    list_filter = ['tipo', 'estado', 'campos_de_conocimiento']
    list_display = ['asignatura', 'clave', 'tipo', 'estado', 'proponente']
    autocomplete_fields = ['proponente',]
    inlines = [NotaInline, ]
    

def publica_curso(modeladmin, request, queryset):
    for c in queryset.all():
        c.status = 'publicado'
        c.save()
    return HttpResponseRedirect(reverse('admin:posgradmin_curso_changelist'))

publica_curso.short_description = "Marcar cursos como publicados"


def concluye_curso(modeladmin, request, queryset):
    for c in queryset.all():
        c.status = 'concluido'
        c.save()

    return HttpResponseRedirect(reverse('admin:posgradmin_curso_changelist'))

concluye_curso.short_description = "Marcar cursos como concluidos"



class CursoAdmin(AutoAutor, VersionAdmin):
    list_display = ['asignatura', 'asignatura_proponente', 'programa', 'lista_academicos',
                    'year', 'semestre', 'intersemestral', 'sede', 'status']
    list_filter = ['year',
                   'semestre',
                   'status',
                   'intersemestral',
                   'sede',
    ]

    inlines = [NotaInline, ]

    search_fields = ['asignatura__asignatura',
                     'academicos__user__first_name',
                     'academicos__user__last_name']

    def lista_academicos(self, obj):
        return ", ".join([str(a) + " (>CP)"
                          if a.acreditacion == 'candidato profesor'
                          else
                          str(a)
                          for a in obj.academicos.all()])

    lista_academicos.short_description = "Académicos"

    def programa(self, obj):
        return format_html("<a href='%s'>programa</a>" % obj.asignatura.programa.url)

    programa.short_description = "Programa"


    def asignatura_proponente(self, obj):
        a = obj.asignatura
        if a.proponente:
            return a.proponente.get_full_name()
        else:
            return None

    asignatura_proponente.short_description = "Propuesta por"
    
    
    autocomplete_fields = ['academicos',]
    readonly_fields = ['profesores', 'contacto', ]

    actions = [publica_curso,
               concluye_curso,
               exporta_emails_cursos,
    ]



admin.site.register(Curso, CursoAdmin)


class InstitucionAdmin(VersionAdmin):
    search_fields = ['nombre', 'suborganizacion']
    list_filter = ['dependencia_UNAM', 'entidad_PCS']
    list_display = ['nombre', 'suborganizacion', 'dependencia_UNAM']


admin.site.register(Institucion, InstitucionAdmin)



class AdscripcionInline(admin.TabularInline):
    model = Adscripcion
    fk_name = 'perfil'
    extra = 1


class PerfilAdmin(AutoAutor, VersionAdmin):
    list_display = [
        'fullname',
        'telefono',
        'email',
        'perfil_comite',
       ]
    search_fields = ['user__first_name', 'user__last_name']

    inlines = [AdscripcionInline, NotaInline, ]

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


class GradosInline(admin.TabularInline):
    model = GradoAcademico
    fk_name = 'user'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    fields = ['fecha_obtencion', 'nivel', 'grado_obtenido', 'institucion']


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline, GradosInline, AnexoExpedienteInline]
    ordering = ('username', 'first_name', 'last_name', '-date_joined')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(CampoConocimiento)
admin.site.register(LineaInvestigacion)

@admin.register(Proyecto)
class ProyectoAdmin(VersionAdmin):
    search_fields = ['estudiante__cuenta',
                     'estudiante__user__first_name',
                     'estudiante__user__last_name',
                     'estudiante__user__email',
                     'fecha',
                     'titulo']
    autocomplete_fields = ['estudiante',]
    list_display = ['fecha', 'plan', 'estudiante', 'titulo',]
    list_filter = ['plan',]    



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



class AcreditacionAdmin(VersionAdmin):
    list_display = ['acreditacion', 'academico', 'fecha']
    search_fields = ['academico__user__username',
                     'academico__user__first_name',
                     'academico__user__last_name', ]
    list_filter = ['acreditacion', ]

admin.site.register(Acreditacion, AcreditacionAdmin)



class ConvocatoriaCursoAdmin(AutoAutor, VersionAdmin):
    list_display = ['year', 'semestre', 'status', 'panel']
    list_filter = ['status', ]
    inlines = [NotaInline, ]

    def panel(self, convocatoria):
        path = reverse('panel_convocatoria_cursos',
                       args=(convocatoria.id,))
        return format_html("<a href='%s'>panel</a>" % path)

    panel.short_description = u'Panel para revisión por CA'
    
admin.site.register(ConvocatoriaCurso, ConvocatoriaCursoAdmin)
