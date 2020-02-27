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
from django.forms.models import model_to_dict


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
            qs = qs.filter(Q(user__first_name__istartswith=self.q)
                           | Q(user__last_name__icontains=self.q))

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
        if auth.is_academico(self.request.user):
            if self.request.user.academico.acreditacion in ['D', 'M', 'P', 'E',
                                                            'candidato profesor']:
                return True
        return False


    def get(self, request, *args, **kwargs):

        convocatoria = models.ConvocatoriaCurso.objects.get(pk=int(kwargs['pk']))

        if convocatoria.status == 'cerrada':
            return HttpResponseRedirect(reverse('mis_cursos'))
        
        asignatura = models.Asignatura.objects.get(pk=int(kwargs['as_id']))
        form = self.form_class(initial={'academicos': [request.user.academico, ]})
        
        breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),
                       (reverse('elige_asignatura', args=[convocatoria.id,]),
                            "Convocatoria para cursos %s-%s" % (convocatoria.year, convocatoria.semestre))
                      )
                               
        return render(request,
                      self.template,
                      {
                          'title': 'Solicitar curso',
                          'breadcrumbs': breadcrumbs,
                          'convocatoria': convocatoria,
                          'asignatura': asignatura,
                          'form': form
                       })


    def post(self, request, *args, **kwargs):
        convocatoria = models.ConvocatoriaCurso.objects.get(pk=int(kwargs['pk']))
        if convocatoria.status == 'cerrada':
            return HttpResponseRedirect(reverse('mis_cursos'))
        
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

            return HttpResponseRedirect(reverse('mis_cursos'))




class CursoView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/solicita_curso.html'
    form_class = forms.CursoModelForm
    
    def test_func(self):

        curso = models.Curso.objects.get(pk=int(self.kwargs['pk']))        
        if auth.is_academico(self.request.user):
            if self.request.user.academico.acreditacion in ['D', 'M', 'P', 'E',
                                                            'candidato profesor']:
                if self.request.user.academico in curso.academicos.all():
                    return True
        return False

    
    def get(self, request, *args, **kwargs):

        curso = models.Curso.objects.get(pk=int(kwargs['pk']))
        form = self.form_class(initial=model_to_dict(curso))
        breadcrumbs = ((reverse('inicio'), 'Inicio'),
                       (reverse('mis_cursos'), "Mis cursos"))
                               
        return render(request,
                      self.template,
                      {
                          'title': 'Editar curso',
                          'breadcrumbs': breadcrumbs,
                          'convocatoria': curso.convocatoria,
                          'asignatura': curso.asignatura,
                          'form': form
                       })


    def post(self, request, *args, **kwargs):
        curso = models.Curso.objects.get(pk=int(kwargs['pk']))        
        convocatoria = curso.convocatoria
        if convocatoria.status == 'cerrada':
            return HttpResponseRedirect(reverse('mis_cursos'))
        
        asignatura = curso.asignatura

        
        form = self.form_class(request.POST)
        if form.is_valid():
            curso.sede = request.POST['sede']
            curso.aula = request.POST['aula']
            curso.horario = request.POST['horario']
            curso.save()

            curso.academicos.clear()
            for ac_id in request.POST.getlist('academicos'):
                ac = models.Academico.objects.get(pk=int(ac_id))
                curso.academicos.add(ac)
            curso.save()

            return HttpResponseRedirect(reverse('mis_cursos'))
        

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

        breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),
                       ('', "Convocatoria para cursos %s-%s" % (convocatoria.year, convocatoria.semestre))
                      )
        
        return render(request,
                      self.template,
                      {
                          'title': 'Asignaturas',
                          'breadcrumbs': breadcrumbs,
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



class MisCursos(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return auth.is_academico(self.request.user)

    model = models.Curso
    template_name = 'posgradmin/mis_cursos_list.html'

    def get_queryset(self):
        new_context = self.request.user.academico.curso_set.all()

        return new_context



    
