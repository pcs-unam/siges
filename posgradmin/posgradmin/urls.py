# coding: utf-8

from django.urls import re_path, include
from django.contrib import admin

from posgradmin.views import PerfilEditar, PerfilDetail, \
    PerfilAcademicoDetail, PerfilProfesorDetail, PerfilProfesorEditar,\
    AcademicoActividadView, AcademicoResumenCVView, AcademicoPerfilView, \
    InicioView, \
    GradoAcademicoAgregar, GradoAcademicoEliminar, InstitucionAgregarView, \
    AdscripcionEliminar, AdscripcionAgregar, AsociacionAgregar, \
    EstudianteSortableView, AcademicoSortableView, \
    UserDetail, PerfilComite, \
    PerfilEstudianteDetail, AcademicoInvitar, AcademicoSearch, \
    TogglePerfilEditar

from posgradmin.views_academico import \
    MisEstudiantesView, EligeAsignatura, SolicitaCurso, \
    AcademicoAutocomplete, CursoView, MisCursos, ProponerAsignatura, CursoConstancia, CursoConstanciaEstudiante

from posgradmin.views_estudiante import CambiarProyectoView

from posgradmin.views_asistente import SesionesListView, SesionDetail # EstudianteCargar

from posgradmin.views_solicitud import SolicitudCambiarEstado, \
    SolicitudNuevaView, SolicitudDetail, SolicitudDictaminar, \
    SolicitudComment, SolicitudAgendar, \
    SolicitudAnexo, SolicitudSortableView

from django.conf.urls.static import static

from posgradmin.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    re_path(r'^admin/posgradmin/toggle_perfil_editar/', TogglePerfilEditar.as_view(),
        name="toggle_perfil_editar"),

    re_path(r'^admin/posgradmin/academico/invitar/', AcademicoInvitar.as_view(),
        name="academico_invitar"),

    re_path(r'^admin/', admin.site.urls),

    re_path('^accounts/', include('allauth.urls')),

    re_path(r'^export_action/', include(("export_action.urls", 'export_action'),
                                     namespace="export_action")),

    re_path(r'^institucion/agregar/(?P<devolver>[\w-]+)/',
        InstitucionAgregarView.as_view(),
        name="agregar_institucion"),

    re_path(r'^inicio/academico/perfil',
        AcademicoPerfilView.as_view(),
        name="academico_perfil"),

    re_path(r'^inicio/academico/resumen',
        AcademicoResumenCVView.as_view(),
        name="academico_resumen"),

    re_path(r'^inicio/academico/actividad',
        AcademicoActividadView.as_view(),
        name="academico_actividad"),

    re_path(r'^inicio/perfil/editar$',
        PerfilEditar.as_view(),
        name="editar_perfil"),

    re_path(r'^inicio/perfil/eliminar-grado/(?P<pk>[0-9]+)$',
        GradoAcademicoEliminar.as_view(),
        name="eliminar_grado"),

    re_path(r'^inicio/perfil/eliminar-adscripcion/(?P<pk>[0-9]+)$',
        AdscripcionEliminar.as_view(),
        name="eliminar_adscripcion"),

    re_path(r'^inicio/perfil/agregar-grado$',
        GradoAcademicoAgregar.as_view(),
        name="agregar_grado"),

    re_path(r'^inicio/perfil/agregar-adscripcion$',
        AdscripcionAgregar.as_view(),
        name="agregar_adscripcion"),

    re_path(r'^inicio/perfil/agregar-asociacion$',
        AsociacionAgregar.as_view(),
        name="agregar_asociacion"),

    re_path(r'^inicio/perfil/comite/(?P<username>.+)$',
        PerfilComite.as_view(),
        name="perfilcomite"),

    re_path(r'^inicio/perfil/$',
        PerfilDetail.as_view(),
        name='perfil'),

    re_path(r'^inicio/perfil-estudiante/$',
        PerfilEstudianteDetail.as_view(),
        name='perfil_estudiante'),

    re_path(r'^inicio/perfil-academico/$',
        PerfilAcademicoDetail.as_view(),
        name='perfil_academico'),

    re_path(r'^inicio/perfil-profesor/$',
        PerfilProfesorDetail.as_view(),
        name='perfil_profesor'),

    re_path(r'^inicio/perfil-profesor/editar',
        PerfilProfesorEditar.as_view(),
        name="perfil_profesor_editar"),

    re_path(r'^inicio/estudiantes/mis$',
        MisEstudiantesView.as_view(),
        name="mis_estudiantes"),

    # re_path(r'^inicio/estudiantes/cargar$',
    #     EstudianteCargar.as_view(),
    #     name="cargar_estudiantes"),

    re_path(r'^inicio/estudiantes/$',
        EstudianteSortableView.as_view(),
        name="lista_estudiantes"),

    re_path(r'^inicio/academicos/$',
        AcademicoSortableView.as_view(),
        name="lista_academicos"),

    re_path(r'^inicio/academicos/search/$',
        AcademicoSearch.as_view(),
        name="academicos_search"),

    # re_path(r'^inicio/catedras/$',
    #     CatedraSortableView.as_view(),
    #     name="lista_catedras"),

    re_path(r'^inicio/solicitudes/$',
        SolicitudSortableView.as_view(),
        name="solicitudes"),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/dictaminar$',
        SolicitudDictaminar.as_view(),
        name="dictaminar"),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/comentar$',
        SolicitudComment.as_view()),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/agendar$',
        SolicitudAgendar.as_view()),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/estado/(?P<estado>[\w-]+)$',
        SolicitudCambiarEstado.as_view()),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/anexar$',
        SolicitudAnexo.as_view()),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/cambiar-proyecto$',
        CambiarProyectoView.as_view(),
        name="cambiar_proyecto"),

    re_path(r'^inicio/solicitudes/(?P<pk>[0-9]+)/$',
        SolicitudDetail.as_view(),
        name="solicitud_detail"),

    re_path(r'^inicio/solicitudes/e/([\w-]+)/$',
        SolicitudSortableView.as_view(),
        name="solicitudes_estado"),

    re_path(r'^inicio/solicitudes/nueva',
        SolicitudNuevaView.as_view(),
        name='solicitud_nueva'),

    re_path(r'^inicio/$',
        InicioView.as_view(),
        name="inicio"),

    re_path(r'^inicio/sesiones/(?P<pk>[0-9]+)/$',
        SesionDetail.as_view(),
        name="sesion_detail"),

    re_path(r'^inicio/sesiones/$',
        SesionesListView.as_view(),
        name='lista_sesiones'),

    re_path(r'^inicio/usuario/(?P<pk>[0-9]+)/$',
        UserDetail.as_view(),
        name="user_detail"),

    re_path('^inicio/', InicioView.as_view()),

    re_path(
        r'^academico-autocomplete/$',
        AcademicoAutocomplete.as_view(),
        name='academico-autocomplete',
        ),

    re_path('^convocatoria-cursos/(?P<pk>[0-9]+)/asignatura/(?P<as_id>[0-9]+)/',
        SolicitaCurso.as_view(),
        name="solicita_curso"),

    re_path('^convocatoria-cursos/(?P<pk>[0-9]+)/',
        EligeAsignatura.as_view(),
        name="elige_asignatura"),

    re_path('^cursos/mis/',
        MisCursos.as_view(),
        name="mis_cursos"),

    re_path('^cursos/(?P<pk>[0-9]+)/constancia-estudiante/',
        CursoConstanciaEstudiante.as_view(),
        name="curso_constancia_estudiante"),

    re_path('^cursos/(?P<pk>[0-9]+)/constancia/',
        CursoConstancia.as_view(),
        name="curso_constancia"),
    
    re_path('^cursos/(?P<pk>[0-9]+)/',
        CursoView.as_view(),
        name="curso"),

    re_path('^proponer-asignatura/',
        ProponerAsignatura.as_view(),
        name="proponer_asignatura"),


] + static(MEDIA_URL, document_root=MEDIA_ROOT)


# ./coordinacion/alimentar_saep.md
# ./coordinacion/oficios_para_firma_de_los_miembros_del_Jurado.md
