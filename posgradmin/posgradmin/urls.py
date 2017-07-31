# coding: utf-8
"""posgradmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from posgradmin.views import SolicitudNuevaView, \
    SolicitudDetail, SolicitudSortableView, \
    PerfilRegistroView, PerfilDetail, EstudianteRegistroView, \
    AcademicoRegistroView, InicioView, SolicitudComment, SolicitudAnexo, \
    GradoAcademicoAgregar, GradoAcademicoEliminar, InstitucionAgregarView, \
    ComiteTutoralElegirView, JuradoCandidaturaElegirView, \
    JuradoGradoElegirView, CambiarProyectoView, MisCursosView, \
    CursoRegistrar, AdscripcionEliminar, AdscripcionAgregar, \
    SolicitudCambiarEstado, SolicitudDictaminar

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),

    url(r'^institucion/agregar',
        InstitucionAgregarView.as_view()),

    url(r'^inicio/estudiante/registro',
        EstudianteRegistroView.as_view()),

    url(r'^inicio/academico/registro',
        AcademicoRegistroView.as_view()),

    url(r'^inicio/perfil/editar$',
        PerfilRegistroView.as_view()),

    url(r'^inicio/perfil/eliminar-grado/(?P<pk>[0-9]+)$',
        GradoAcademicoEliminar.as_view()),

    url(r'^inicio/perfil/eliminar-adscripcion/(?P<pk>[0-9]+)$',
        AdscripcionEliminar.as_view()),

    url(r'^inicio/perfil/agregar-grado$',
        GradoAcademicoAgregar.as_view()),

    url(r'^inicio/perfil/agregar-adscripcion$',
        AdscripcionAgregar.as_view()),

    url(r'^inicio/perfil/$',
        PerfilDetail.as_view()),

    url(r'^inicio/solicitudes/$',
        SolicitudSortableView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/dictaminar$',
        SolicitudDictaminar.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/comentar$',
        SolicitudComment.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/estado/(?P<estado>[\w-]+)$',
        SolicitudCambiarEstado.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/anexar$',
        SolicitudAnexo.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/elegir-comite-tutoral$',
        ComiteTutoralElegirView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/elegir-jurado-candidatura$',
        JuradoCandidaturaElegirView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/elegir-jurado-grado$',
        JuradoGradoElegirView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/cambiar-proyecto$',
        CambiarProyectoView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/$',
        SolicitudDetail.as_view()),

    url(r'^inicio/solicitudes/e/([\w-]+)/$',
        SolicitudSortableView.as_view()),

    url(r'^inicio/solicitudes/nueva',
        SolicitudNuevaView.as_view()),

    url(r'^inicio/$',
        InicioView.as_view()),

    url(r'^inicio/cursos/mis_cursos$',
        MisCursosView.as_view()),
    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/registrar-curso$',
        CursoRegistrar.as_view()),


# ./coordinacion/ratificacion_predictamenes.md
# ./coordinacion/alimentar_saep.md
# ./coordinacion/administrar_sesiones_ca.md
# ./coordinacion/oficios_para_firma_de_los_miembros_del_Jurado.md
]

# ./README.md
# ./registrar_curso.md
# ./proceso_de_admision.md~
# ./README.md~
# ./academicos
# ./academicos/predictaminar_propuesta_comitetutoral.md
# ./academicos/asentir_suspensión.md
# ./academicos/README.md
# ./academicos/registrar_curso.md
# ./academicos/validacion_actividad_complementaria.md
# ./academicos/registrar_curso.md~
# ./academicos/solicitud_de_apoyo_economico.md
# ./academicos/registrar_profesor_como_tutor.md~
# ./academicos/registrar_profesor_como_tutor.md
# ./academicos/predictaminar_propuestas_de_comite_tutoral.md
# ./academicos/revision_comentarios_solicitudes.md
# ./academicos/secretario_dictamina_la_evaluacion_de_candidatura.md
# ./academicos/jurado_candidatura.md
# ./academicos/respuesta_a_la_solicitud_del_alumno.md
# ./academicos/autorizar_curso.md
# ./academicos/confirmacion_para_ser_tutor.md
# ./estudiantes
# ./estudiantes/cambio_titulo_proyecto.md
# ./estudiantes/solicitud_candidatura.md
# ./estudiantes/README.md
# ./estudiantes/solicitud_suspension.md
# ./estudiantes/fecha_exame_candidatura.md
# ./estudiantes/solicitud_cambio_campo.md
# ./estudiantes/cambio_comite_tutoral.md
# ./estudiantes/registro_actividad_complementaria.md
# ./estudiantes/seleccion_comite_tutoral.md
