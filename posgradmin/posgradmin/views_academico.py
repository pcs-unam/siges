# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.views import View
from django.db.models import Q
import posgradmin.models as models
from posgradmin import authorization as auth
from django.conf import settings
from django.shortcuts import render, HttpResponseRedirect
import posgradmin.forms as forms
from dal import autocomplete

from pprint import pprint

class AcademicoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return models.Academico.objects.none()

        qs = models.Academico.objects.all()

        if self.q:
            qs = qs.filter(user__first_name__istartswith=self.q)

        return qs


# class MisCatedrasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     login_url = settings.APP_PREFIX + 'accounts/login/'

#     def test_func(self):
#         return auth.is_academico(self.request.user)

#     model = models.Catedra

#     def get_queryset(self):
#         new_context = models.Catedra.objects.filter(
#             profesor=self.request.user.academico
#         )
#         return new_context


class SolicitaCurso(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/solicita_curso.html'
    form_class = forms.CursoModelForm

    def test_func(self):
        return auth.is_academico(self.request.user)

    def get(self, request, *args, **kwargs):

        convocatoria = models.ConvocatoriaCurso.objects.get(pk=int(kwargs['pk']))
        asignatura = models.Asignatura.objects.get(pk=int(kwargs['as_id']))
        
        return render(request,
                      self.template,
                      {
                          'title': 'Asignaturas',
                          'convocatoria': convocatoria,
                          'asignatura': asignatura,
                          'form': self.form_class
                       })


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            print(request.POST['sede'],
                  request.POST['academicos'],
                  request.POST['aula'],
                  request.POST['horario'])        
            return HttpResponseRedirect(reverse('inicio'))
    

class EligeAsignatura(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/elige_asignatura.html'

    def test_func(self):
        return auth.is_academico(self.request.user)


    def get(self, request, *args, **kwargs):


        pk = int(kwargs['pk'])
        convocatoria = models.ConvocatoriaCurso.objects.get(pk=pk)

        asignaturas = models.Asignatura.objects.filter(
            Q(tipo='Optativa') &
            (Q(estado='aceptada') | Q(estado='propuesta')))

        return render(request,
                      self.template,
                      {
                          'title': 'Asignaturas',
                          'asignaturas': asignaturas,
                          'convocatoria': convocatoria,
                       })

    
class MisComitesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return auth.is_academico(self.request.user)

    model = models.Comite
    template_name = 'posgradmin/comite_list.html'

    def get_queryset(self):
        new_context = self.request.user.academico.comites()

        return new_context


class MisEstudiantesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return auth.is_academico(self.request.user)

    model = models.Estudiante
    template_name = 'posgradmin/mis_estudiantes_list.html'

    def get_queryset(self):
        new_context = self.request.user.academico.estudiantes()

        return new_context
