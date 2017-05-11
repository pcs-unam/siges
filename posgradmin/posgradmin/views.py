# coding: utf-8

from django.views.generic import ListView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from posgradmin.models import Asunto, Anexo, Perfil, Estudiante, Academico
from posgradmin.forms import AsuntoForm, PerfilModelForm, EstudianteModelForm, AcademicoModelForm
from pprint import pprint


class InicioView(View):

    breadcrumbs = (('/inicio/', 'Inicio'),)

    template_name = 'posgradmin/inicio.html'

    def get(self, request, *args, **kwargs):
        return render(request,
                      self.template_name,
                      {'title': 'Inicio',
                       'breadcrumbs': self.breadcrumbs})




asuntos_profesoriles = (
        ("registrar_curso",
         "Registrar Curso"),
        ("solicitar_registro_como_tutor",
         "Solicitar Registro como Tutor"),
        ("solicitar_apoyo_económico",
         "Solicitar Apoyo Económico"),
        ("generar_reporte_actividades",
         "Generar Reporte de Actividades"))

asuntos_tutoriles = (
        ("solicitar_baja_tutor",
         "Solicitar Baja de Tutoría en el Programa"),
        ("avisar_ausencia",
         "Aviso de Ausencia por Sabático u Otra Razón"))

asuntos_estudiantiles = (
        ('seleccionar_jurado',
         "Selección de jurado de grado o de candidatura"),
        ('registrar_actividad_complementaria',
         "Registro de actividad complementaria"),
        ('solicitar_candidatura',
         "Solicitud de examen de candidtaura"),
        ("cambiar_comite_tutoral",
         "Cambiar comité tutoral"),
        ("cambiar_titulo_proyecto",
         "Solicitud de cambio de título de proyecto"),
        ("cambiar_campo_conocimiento",
         "Cambio de campo de conocimiento"),
        ("reportar_suspension",
         "Reportar suspensión"))

asunto_otro = (
    ('otro',
     'Otro'),)


class AsuntoNuevoView(View):

    form_class = AsuntoForm
    form_class.base_fields['tipo'].choices = asuntos_profesoriles + \
                                             asuntos_tutoriles + \
                                             asunto_otro

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/asuntos/', 'Asuntos'),
                   ('/inicio/asuntos/nuevo', 'Nuevo'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Asunto nuevo',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            a = Asunto()
            a.resumen = request.POST['resumen']
            a.tipo = request.POST['tipo']
            a.solicitante = request.user
            a.descripcion = request.POST['descripcion']
            a.estado = 'nuevo'
            a.save()

            if 'anexo' in request.FILES:
                nx = Anexo(asunto=a,
                           archivo=request.FILES['anexo'])
                nx.save()

            return HttpResponseRedirect('/asuntos/%s' % a.id)
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Asunto nuevo',
                           'breadcrumbs': self.breadcrumbs})


class AsuntoList(ListView):
    model = Asunto


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

    form_class = EstudianteModelForm

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
