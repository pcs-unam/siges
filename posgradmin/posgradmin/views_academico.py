# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
import posgradmin.models as models


class MisCatedrasView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    def test_func(self):
        if hasattr(self.request.user, 'academico'):
            return True
        else:
            return False

    model = models.Catedra

    def get_queryset(self):
        new_context = models.Catedra.objects.filter(
            profesor=self.request.user.academico
        )
        return new_context


class MisComitesView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    def test_func(self):
        return True

    model = models.Comite
    template_name = 'posgradmin/comite_list.html'

    def get_queryset(self):
        new_context = self.request.user.academico.comites()

        return new_context


class MisEstudiantesView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    def test_func(self):
        return True

    model = models.Estudiante
    template_name = 'posgradmin/mis_estudiantes_list.html'

    def get_queryset(self):
        new_context = self.request.user.academico.estudiantes()

        return new_context
