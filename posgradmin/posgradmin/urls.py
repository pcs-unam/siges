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

from posgradmin.views import PerfilRegistroView, PerfilDetail, \
    AcademicoRegistroView, InicioView, \
    GradoAcademicoAgregar, GradoAcademicoEliminar, InstitucionAgregarView, \
    AdscripcionEliminar, AdscripcionAgregar, \
    EstudianteSortableView, AcademicoSortableView, CatedraSortableView, \
    UserDetail

from posgradmin.views_academico import MisCatedrasView, \
    MisComitesView, MisEstudiantesView

from posgradmin.views_estudiante import ComiteTutoralElegirView, \
    JuradoCandidaturaElegirView, \
    JuradoGradoElegirView, CambiarProyectoView

from posgradmin.views_asistente import SesionesListView, SesionDetail, \
    CatedraRegistrar, EstudianteCargar

from posgradmin.views_solicitud import SolicitudCambiarEstado, \
    SolicitudNuevaView, SolicitudDetail, SolicitudDictaminar, \
    SolicitudComment, SolicitudAgendar, \
    SolicitudAnexo, SolicitudSortableView

from django.conf.urls.static import static

from posgradmin.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),

    url(r'^institucion/agregar',
        InstitucionAgregarView.as_view()),

    url(r'^inicio/usuario/(?P<pk>[0-9]+)/$',
        UserDetail.as_view()),

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

    url(r'^inicio/estudiantes/mis$',
        MisEstudiantesView.as_view()),

    url(r'^inicio/estudiantes/cargar$',
        EstudianteCargar.as_view()),

    url(r'^inicio/estudiantes/$',
        EstudianteSortableView.as_view()),

    url(r'^inicio/academicos/$',
        AcademicoSortableView.as_view()),

    url(r'^inicio/catedras/$',
        CatedraSortableView.as_view()),

    url(r'^inicio/solicitudes/$',
        SolicitudSortableView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/dictaminar$',
        SolicitudDictaminar.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/comentar$',
        SolicitudComment.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/agendar$',
        SolicitudAgendar.as_view()),

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

    url(r'^inicio/catedras/mis$',
        MisCatedrasView.as_view()),

    url(r'^inicio/comites/mis$',
        MisComitesView.as_view()),

    url(r'^inicio/solicitudes/(?P<pk>[0-9]+)/registrar-catedra$',
        CatedraRegistrar.as_view()),

    url(r'^inicio/sesiones/(?P<pk>[0-9]+)/$',
        SesionDetail.as_view()),

    url(r'^inicio/sesiones/$',
        SesionesListView.as_view()),

] + static(MEDIA_URL, document_root=MEDIA_ROOT)


# ./coordinacion/alimentar_saep.md
# ./coordinacion/oficios_para_firma_de_los_miembros_del_Jurado.md
