# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
import posgradmin.models as models
import posgradmin.forms as forms


class ComiteElegirView(View):
    def test_func(self):
        return True

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
            comite = models.Comite(estudiante=request.user.estudiante,
                                   solicitud=models.Solicitud.objects.get(
                                       id=int(kwargs['pk'])),
                                   tipo=self.tipo,
                                   presidente=presidente,
                                   secretario=secretario,
                                   vocal=vocal)
            comite.save()

            return HttpResponseRedirect('/inicio/solicitudes/%s/'
                                        % solicitud.id)
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Elegir Comité Tutoral',
                           'form': form,
                           'breadcrumbs':
                           self.get_breadcrumbs(int(kwargs['pk']))})


class ComiteTutoralElegirView(LoginRequiredMixin,
                              UserPassesTestMixin,
                              ComiteElegirView):

    def test_func(self):
        return True

    tipo = 'tutoral'
    title = 'Elegir Comité Tutoral'

    def get_breadcrumbs(self, pk):
        solicitud = models.Solicitud.objects.get(id=pk)
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                ('/inicio/solicitudes/%s/elegir-comite-tutoral'
                 % solicitud.id, 'Elegir Comité Tutoral')]


class JuradoCandidaturaElegirView(LoginRequiredMixin,
                                  UserPassesTestMixin,
                                  ComiteElegirView):
    tipo = 'candidatura'
    title = 'Elegir Jurado para Candidatura'

    def get_breadcrumbs(self, pk):
        solicitud = models.Solicitud.objects.get(id=pk)
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                ('/inicio/solicitudes/%s/elegir-jurado-candidatura'
                 % solicitud.id, 'Elegir Jurado para Candidatura')]


class JuradoGradoElegirView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            ComiteElegirView):

    def test_func(self):
        return True

    tipo = 'grado'
    title = 'Elegir Jurado para Examen de Grado'

    def get_breadcrumbs(self, pk):
        solicitud = models.Solicitud.objects.get(id=pk)
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                ('/inicio/solicitudes/%s/elegir-jurado-grado'
                 % solicitud.id, 'Elegir Jurado para Examen de Grado')]


class CambiarProyectoView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return True

    form_class = forms.ProyectoModelForm
    template_name = 'posgradmin/try.html'

    def get_breadcrumbs(self, pk):
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % pk,
                 '#%s' % pk),
                ('/inicio/solicitudes/%s/cambiar-proyecto'
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

            return HttpResponseRedirect("/inicio/solicitudes/%s"
                                        % solicitud.id)
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Cambios al Proyecto',
                           'form': form,
                           'breadcrumbs': self.get_breadcrumbs(kwargs['pk'])})
