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
from django.urls import reverse


class AcademicoAutocomplete(LoginRequiredMixin, UserPassesTestMixin, autocomplete.Select2QuerySetView):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if auth.is_academico(self.request.user):
            if self.request.user.academico.acreditacion in ['D', 'M', 'P', 'E',
                                                            'candidato profesor']:
                return True
        return False

    
    def get_queryset(self):

        qs = models.Academico.objects.filter(Q(acreditacion='candidato profesor')
                                             | Q(acreditacion='P')
                                             | Q(acreditacion='M')
                                             | Q(acreditacion='D')
                                             | Q(acreditacion='E'))

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
        form = self.form_class(initial={'academicos': [request.user.academico, ]})
                               
        return render(request,
                      self.template,
                      {
                          'title': 'Asignaturas',
                          'convocatoria': convocatoria,
                          'asignatura': asignatura,
                          'form': form
                       })


    def post(self, request, *args, **kwargs):
        convocatoria = models.ConvocatoriaCurso.objects.get(pk=int(kwargs['pk']))
        asignatura = models.Asignatura.objects.get(pk=int(kwargs['as_id']))
        form = self.form_class(request.POST)
        if form.is_valid():
            curso = models.Curso(
                convocatoria=convocatoria,
                asignatura=asignatura,
                year=convocatoria.year,
                semestre=convocatoria.semestre,
                sede=request.POST['sede'],
                aula=request.POST['aula'],
                horario=request.POST['horario'])
            curso.save()

            for ac_id in request.POST.getlist('academicos'):
                ac = models.Academico.objects.get(pk=int(ac_id))
                curso.academicos.add(ac)
            curso.academicos.add(request.user.academico)
            curso.save()

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
