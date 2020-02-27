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


class EligeAsignatura(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/elige_asignatura.html'

    def test_func(self):
        return auth.is_academico(self.request.user)


    def get(self, request, *args, **kwargs):


        pk = int(kwargs['pk'])
        print(pk)
        asignaturas = models.Asignatura.objects.filter(
            Q(estado='aceptada') | Q(estado='propuesta'))

        return render(request,
                      self.template,
                      {
                       'title': 'Asignaturas',
                       'asignaturas': asignaturas
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
