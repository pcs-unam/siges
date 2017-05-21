# coding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from posgradmin.models import Solicitud, Anexo, Perfil, Estudiante, \
    Academico, CampoConocimiento
from posgradmin.forms import SolicitudForm, PerfilModelForm, \
    AcademicoModelForm, EstudianteAutoregistroForm
from settings import solicitudes_profesoriles,\
    solicitudes_tutoriles, solicitudes_estudiantiles, solicitud_otro
from posgradmin import workflows

from pprint import pprint


class InicioView(View):

    breadcrumbs = (('/inicio/', 'Inicio'),)

    template_name = 'posgradmin/inicio.html'

    def get(self, request, *args, **kwargs):

        solicitudes = {}
        # TODO: alguien podria ser estudiante y académico simultaneamente
        try:
            solicitudes = request.user.academico.cuantas_solicitudes()
        except ObjectDoesNotExist:
            pass

        try:
            request.user.estudiante
            solicitudes = {'todas':
                           request.user.estudiante.solicitudes().count(),
                           'nuevas':
                           request.user.estudiante.solicitudes(
                               estado='nueva').count()
                           }
        except ObjectDoesNotExist:
            pass

        return render(request,
                      self.template_name,
                      {'title': 'Inicio',
                       'solicitudes': solicitudes,
                       'breadcrumbs': self.breadcrumbs})


class SolicitudNuevaView(View):

    form_class = SolicitudForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/solicitudes/', 'Solicitudes'),
                   ('/inicio/solicitudes/nueva', 'Nueva'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):

        choices = []
        # opciones de academico
        try:
            a = request.user.academico
            if a.tutor:
                choices += solicitudes_tutoriles
            else:
                choices += (("solicitar_registro_como_tutor",
                             "Solicitar Registro como Tutor"),)

            if a.profesor:
                choices += solicitudes_profesoriles

        except ObjectDoesNotExist:
            pass
        # opciones de estudiante
        try:
            request.user.estudiante
            choices += solicitudes_estudiantiles
        except ObjectDoesNotExist:
            pass

        choices += solicitud_otro

        self.form_class.base_fields['tipo'].choices = choices

        form = self.form_class()

        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Nueva solicitud',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            s = Solicitud()
            s.resumen = request.POST['resumen']
            s.tipo = request.POST['tipo']
            s.solicitante = request.user
            s.descripcion = request.POST['descripcion']
            s.save()

            if 'anexo' in request.FILES:
                nx = Anexo(solicitud=s,
                           archivo=request.FILES['anexo'])
                nx.save()

            next = workflows.solicitud.get(s.estado,
                                           '/solicitudes/%s')
            return HttpResponseRedirect(next % s.id)
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Solicitud nueva',
                           'breadcrumbs': self.breadcrumbs})


class SolicitudList(ListView):
    model = Solicitud


class PerfilRegistroView(View):

    form_class = PerfilModelForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/perfil/', 'Perfil'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Completar Perfil',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            p = Perfil()
            p.user = request.user
            p.fecha_nacimiento = request.POST['fecha_nacimiento']
            p.genero = request.POST['genero']
            p.nacionalidad = request.POST['nacionalidad']
            p.curp = request.POST['curp']
            p.rfc = request.POST['rfc']
            p.telefono = request.POST['telefono']
            p.telefono_movil = request.POST['telefono_movil']
            p.email2 = request.POST['email2']
            p.website = request.POST['website']
            p.direccion1 = request.POST['direccion1']
            p.direccion2 = request.POST['direccion2']
            p.codigo_postal = request.POST['codigo_postal']
            p.save()

            return HttpResponseRedirect('/perfil/')
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Registrar como Estudiante',
                           'breadcrumbs': self.breadcrumbs})


class EstudianteRegistroView(View):

    form_class = EstudianteAutoregistroForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/estudiante/registro/', 'Registro como estudiante'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Registrarse como Estudiante',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            e = Estudiante()
            e.user = request.user
            e.estado = 'aspirante'
            campo = CampoConocimiento.objects.get(
                id=int(request.POST['campo_conocimiento']))
            print campo
            e.campo_conocimiento = campo
            e.nombre_proyecto = form['proyecto']
            e.save()

            return HttpResponseRedirect('/estudiante/%s' % e.id)
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Registrarse como Estudiante',
                           'breadcrumbs': self.breadcrumbs})


class AcademicoRegistroView(View):

    form_class = AcademicoModelForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/academico/', 'Académico'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Registrarse como Académico',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            a = Academico()
            a.user = request.user
            a.save()

            return HttpResponseRedirect('/academico/%s' % a.id)
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Registrarse como Académico',
                           'breadcrumbs': self.breadcrumbs})
