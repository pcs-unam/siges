# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from sortable_listview import SortableListView
import posgradmin.models as models
import posgradmin.forms as forms
from django.conf import settings

import etl


class SesionesListView(LoginRequiredMixin,
                       UserPassesTestMixin,
                       SortableListView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    allowed_sort_fields = {'fecha': {'default_direction': '-',
                                     'verbose_name': 'fecha'}}
    default_sort_field = 'fecha'
    paginate_by = 15
    model = models.Sesion


class SesionDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    model = models.Sesion


class CatedraRegistrar(LoginRequiredMixin, UserPassesTestMixin, View):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    form_class = forms.CatedraModelForm

    def get_breadcrumbs(self, pk):
        return [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                (settings.APP_PREFIX + 'inicio/solicitudes/', 'Solicitudes'),
                (settings.APP_PREFIX + 'inicio/solicitudes/%s/' % pk,
                 '#%s' % pk),
                (settings.APP_PREFIX
                 + 'inicio/solicitudes/%s/registrar-catedra'
                 % pk, 'Registrar Cátedra')]

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request,
                      self.template_name,
                      {'title': 'Registrar Cátedra',
                       'form': form,
                       'breadcrumbs': self.get_breadcrumbs(kwargs['pk'])})

    def post(self, request, *args, **kwargs):
        sid = int(kwargs['pk'])
        s = models.Solicitud.objects.get(id=sid)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            curso = models.Curso.objects.get(
                id=int(request.POST['curso']))
            c = models.Catedra(curso=curso,
                               year=request.POST['year'],
                               semestre=request.POST['semestre'],
                               solicitud=s)
            c.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(s.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Registrar Curso',
                           'form': form,
                           'breadcrumbs': self.get_breadcrumbs(kwargs['pk'])})


class EstudianteCargar(LoginRequiredMixin, UserPassesTestMixin, View):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        else:
            return False

    form_class = forms.EstudianteCargarForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX
                    + 'inicio/estudiantes/', 'Estudiantes')]

    template_name = 'posgradmin/cargar_lote.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()

        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Cargar lote de estudiantes',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            errores = etl.load(request.FILES['lista'],
                               request.POST['ingreso'],
                               request.POST['semestre'])
            if errores:
                return render(request,
                              self.template_name,
                              {'errores': errores,
                               'form': form,
                               'breadcrumbs': self.breadcrumbs})
            else:
                return HttpResponseRedirect(reverse('lista_estudiantes'))
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'breadcrumbs': self.breadcrumbs})
