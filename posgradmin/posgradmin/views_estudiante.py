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

class ComiteElegirView(View):
    def test_func(self):
        return auth.is_estudiante(self.request.user)

    form_class = forms.ComiteTutoralModelForm

    template_name = 'posgradmin/institucion_agregar.html'

    tipo = 'tutoral'

    def get_breadcrumbs():
        pass

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request,
                      self.template_name,
                      {'title': self.title,
                       'form': form,
                       'breadcrumbs': self.get_breadcrumbs(int(kwargs['pk']))})


class ComiteTutoralElegirView(LoginRequiredMixin,
                              UserPassesTestMixin,
                              ComiteElegirView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return auth.is_estudiante(self.request.user)

    tipo = 'tutoral'
    title = 'Elegir Comité Tutoral'
    form_class = forms.ComiteTutoralModelForm

    def get_breadcrumbs(self, pk):
        solicitud = models.Solicitud.objects.get(id=pk)
        return [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                (settings.APP_PREFIX + 'inicio/solicitudes/', 'Solicitudes'),
                (settings.APP_PREFIX + 'inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                (settings.APP_PREFIX
                 + 'inicio/solicitudes/%s/elegir-comite-tutoral'
                 % solicitud.id, 'Elegir Comité Tutoral')]

    def post(self, request, *args, **kwargs):
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        form = self.form_class(request.POST)
        if form.is_valid():
            tutor = models.Academico.objects.get(
                id=int(request.POST['tutor']))
            cotutor = models.Academico.objects.get(
                id=int(request.POST['cotutor']))
            miembro1 = models.Academico.objects.get(
                id=int(request.POST['miembro1']))

            if request.POST['miembro2']:
                miembro2 = models.Academico.objects.get(
                    id=int(request.POST['miembro2']))
            else:
                miembro2 = None

            if request.POST['miembro3']:
                miembro3 = models.Academico.objects.get(
                    id=int(request.POST['miembro3']))
            else:
                miembro3 = None

            comite = models.Comite(estudiante=request.user.estudiante,
                                   solicitud=models.Solicitud.objects.get(
                                       id=int(kwargs['pk'])),
                                   tipo=self.tipo,
                                   miembro1=tutor,
                                   miembro2=cotutor,
                                   miembro3=miembro1,
                                   miembro4=miembro2,
                                   miembro5=miembro3)
            comite.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Elegir Comité Tutoral',
                           'form': form,
                           'breadcrumbs':
                           self.get_breadcrumbs(int(kwargs['pk']))})


class JuradoCandidaturaElegirView(LoginRequiredMixin,
                                  UserPassesTestMixin,
                                  ComiteElegirView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    tipo = 'candidatura'
    title = 'Elegir Jurado para Candidatura'
    form_class = forms.CandidaturaModelForm

    def test_func(self):
        return auth.is_estudiante(self.request.user)

    def get_breadcrumbs(self, pk):
        solicitud = models.Solicitud.objects.get(id=pk)
        return [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                (settings.APP_PREFIX + 'inicio/solicitudes/', 'Solicitudes'),
                (settings.APP_PREFIX + 'inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                (settings.APP_PREFIX
                 + 'inicio/solicitudes/%s/elegir-jurado-candidatura'
                 % solicitud.id, 'Elegir Jurado para Candidatura')]

    def post(self, request, *args, **kwargs):
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        form = self.form_class(request.POST)
        if form.is_valid():
            presidente = models.Academico.objects.get(
                id=int(request.POST['presidente']))
            secretario = models.Academico.objects.get(
                id=int(request.POST['secretario']))
            if request.POST['miembro1']:
                miembro1 = models.Academico.objects.get(
                    id=int(request.POST['miembro1']))
            else:
                miembro1 = None

            if request.POST['miembro2']:
                miembro2 = models.Academico.objects.get(
                    id=int(request.POST['miembro2']))
            else:
                miembro2 = None

            if request.POST['miembro3']:
                miembro3 = models.Academico.objects.get(
                    id=int(request.POST['miembro3']))
            else:
                miembro3 = None

            comite = models.Comite(estudiante=request.user.estudiante,
                                   solicitud=models.Solicitud.objects.get(
                                       id=int(kwargs['pk'])),
                                   tipo=self.tipo,
                                   miembro1=presidente,
                                   miembro2=secretario,
                                   miembro3=miembro1,
                                   miembro4=miembro2,
                                   miembro5=miembro3)
            comite.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Elegir Jurado para Examen de Candidatura',
                           'form': form,
                           'breadcrumbs':
                           self.get_breadcrumbs(int(kwargs['pk']))})


class JuradoGradoElegirView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            ComiteElegirView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return auth.is_estudiante(self.request.user)

    tipo = 'grado'
    title = 'Elegir Jurado para Examen de Grado'
    form_class = forms.JuradoGradoModelForm

    def get_breadcrumbs(self, pk):
        solicitud = models.Solicitud.objects.get(id=pk)
        return [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                (settings.APP_PREFIX + 'inicio/solicitudes/', 'Solicitudes'),
                (settings.APP_PREFIX + 'inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                (settings.APP_PREFIX
                 + 'inicio/solicitudes/%s/elegir-jurado-grado'
                 % solicitud.id, 'Elegir Jurado para Examen de Grado')]

    def post(self, request, *args, **kwargs):
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        form = self.form_class(request.POST)
        if form.is_valid():
            presidente = models.Academico.objects.get(
                id=int(request.POST['presidente']))
            secretario = models.Academico.objects.get(
                id=int(request.POST['secretario']))
            vocal = models.Academico.objects.get(
                id=int(request.POST['vocal']))
            suplente = models.Academico.objects.get(
                id=int(request.POST['suplente']))

            comite = models.Comite(estudiante=request.user.estudiante,
                                   solicitud=models.Solicitud.objects.get(
                                       id=int(kwargs['pk'])),
                                   tipo=self.tipo,
                                   miembro1=presidente,
                                   miembro2=secretario,
                                   miembro3=vocal,
                                   miembro4=suplente)
            comite.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Elegir Jurado para Examen de Grado',
                           'form': form,
                           'breadcrumbs':
                           self.get_breadcrumbs(int(kwargs['pk']))})


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
