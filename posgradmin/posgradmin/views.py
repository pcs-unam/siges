# coding: utf-8

from django.views.generic import ListView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from posgradmin.models import Asunto, Anexo
from posgradmin.forms import AsuntoForm
from pprint import pprint

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

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Asunto nuevo'})

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
                           'title': 'Asunto nuevo'})


class AsuntoList(ListView):
    model = Asunto
