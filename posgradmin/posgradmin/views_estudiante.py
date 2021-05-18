# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
import posgradmin.models as models
import posgradmin.forms as forms
from posgradmin import authorization as auth
from django.conf import settings



class CambiarProyectoView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return auth.is_estudiante(self.request.user)

    form_class = forms.ProyectoModelForm
    template_name = 'posgradmin/try.html'

    def get_breadcrumbs(self, pk):
        return [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                (settings.APP_PREFIX + 'inicio/solicitudes/', 'Solicitudes'),
                (settings.APP_PREFIX + 'inicio/solicitudes/%s/' % pk,
                 '#%s' % pk),
                (settings.APP_PREFIX + 'inicio/solicitudes/%s/cambiar-proyecto'
                 % pk, 'Cambios al Proyecto')]

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request,
                      self.template_name,
                      {'title': 'Cambios al Proyecto',
                       'form': form,
                       'breadcrumbs': self.get_breadcrumbs(kwargs['pk'])})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        if form.is_valid():
            p = models.\
                Proyecto(nombre=request.POST['nombre'],
                         campo_conocimiento=models.
                         CampoConocimiento.objects.get(
                             id=int(request.POST['campo_conocimiento'])),
                         estudiante=request.user.estudiante,
                         solicitud=solicitud)
            p.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Cambios al Proyecto',
                           'form': form,
                           'breadcrumbs': self.get_breadcrumbs(kwargs['pk'])})
