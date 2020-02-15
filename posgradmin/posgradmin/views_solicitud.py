# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from sortable_listview import SortableListView
from django.conf import settings
import posgradmin.models as models
import posgradmin.forms as forms
from posgradmin import workflows

#from settings import settings.solicitudes_profesoriles,\
#    settings.solicitudes_tutoriles, settings.solicitudes_estudiantiles, settings.solicitud_otro


class SolicitudCambiarEstado(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        elif hasattr(self.request.user, 'academico'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.academico.solicitudes()
        elif hasattr(self.request.user, 'estudiante'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.estudiante.solicitudes()
        else:
            return False

    def get(self, request, *args, **kwargs):
        sid = int(kwargs['pk'])
        s = models.Solicitud.objects.get(id=sid)
        s.estado = kwargs['estado']
        s.save()
        return HttpResponseRedirect(reverse('solicitud_detail',
                                            args=(sid,)))


class SolicitudNuevaView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or hasattr(self.request.user, 'estudiante') \
           or hasattr(self.request.user, 'academico') \
           or self.request.user.is_staff:
            return True
        else:
            return False

    form_class = forms.SolicitudForm

    breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX
                    + 'inicio/solicitudes/', 'Solicitudes'),
                   (settings.APP_PREFIX + 'inicio/solicitudes/nueva', 'Nueva'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):

        choices = []
        # opciones de academico
        try:
            a = request.user.academico
            if a.tutor:
                choices += settings.solicitudes_tutoriles
            elif a.acreditado():
                choices += settings.solicitudes_profesoriles
                choices += (("solicitar_registro_como_tutor",
                             "Solicitar Registro como Tutor"),)

        except ObjectDoesNotExist:
            pass
        # opciones de estudiante
        try:
            request.user.estudiante
            choices += settings.solicitudes_estudiantiles
        except ObjectDoesNotExist:
            pass

        choices += settings.solicitud_otro

        self.form_class.base_fields['tipo'].choices = choices

        form = self.form_class()

        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Nueva solicitud',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            s = models.Solicitud()
            s.resumen = request.POST['resumen']
            s.tipo = request.POST['tipo']
            s.solicitante = request.user
            s.descripcion = request.POST['descripcion']
            s.save()

            if 'anexo' in request.FILES:
                nx = models.Anexo(solicitud=s,
                                  autor=request.user,
                                  archivo=request.FILES['anexo'])
                nx.save()

            next = workflows.solicitud.get(s.tipo,
                                           settings.APP_PREFIX
                                           + 'inicio/solicitudes/%s')
            return HttpResponseRedirect(next % s.id)
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Solicitud nueva',
                           'breadcrumbs': self.breadcrumbs})


class SolicitudDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        elif hasattr(self.request.user, 'academico'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.academico.solicitudes()
        elif hasattr(self.request.user, 'estudiante'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.estudiante.solicitudes()
        else:
            return False

    model = models.Solicitud

    def get_context_data(self, **kwargs):
        context = super(SolicitudDetail, self).get_context_data(**kwargs)
        context['agendable'] = context['object'].agendable(self.request.user)
        context['dictaminable'] = context[
            'object'].dictaminable(self.request.user)
        context[
            'cancelable'] = context['object'].cancelable(self.request.user)
        return context


class SolicitudDictaminar(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        elif hasattr(self.request.user, 'academico'):
            return True  # revisar que sea de estudiante suyo y no suya
        else:
            return False

    form_class = forms.SolicitudDictamenForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX
                    + 'inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_comment.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla
        return render(request,
                      self.template_name,
                      {'object': solicitud,
                       'form': form,
                       'breadcrumbs': self.breadcrumbs.append(
                           (settings.APP_PREFIX
                            + 'inicio/solicitudes/%s/' % solicitud.id,
                            '#%s' % solicitud.id))})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
            c = models.Comentario()
            c.solicitud = solicitud
            c.autor = request.user
            if 'denegar' in request.POST:
                if solicitud.tipo == 'registrar_catedra':
                    ct = solicitud.catedra
                    ct.delete()
                d = models.Dictamen(resolucion='denegada',
                                    solicitud=solicitud,
                                    autor=request.user)
                c.comentario = '## Dictamen: solicitud denegada\n\n'
            elif 'conceder' in request.POST:
                if solicitud.tipo == 'registrar_catedra':
                    ct = solicitud.catedra
                    ct.profesor = solicitud.solicitante.academico
                    ct.save()
                d = models.Dictamen(resolucion='concedida',
                                    solicitud=solicitud,
                                    autor=request.user)
                c.comentario = '## Dictamen: solicitud concedida\n\n'
            d.save()

            c.comentario += request.POST['comentario']
            c.save()

            if request.user.is_staff or hasattr(request.user, 'asistente'):
                solicitud.estado = 'atendida'
            solicitud.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class SolicitudComment(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        elif hasattr(self.request.user, 'academico'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.academico.solicitudes()
        elif hasattr(self.request.user, 'estudiante'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.estudiante.solicitudes()
        else:
            return False

    form_class = forms.SolicitudCommentForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX
                    + 'inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_comment.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'object': solicitud,
                       'form': form,
                       'breadcrumbs': self.breadcrumbs.append(
                           (settings.APP_PREFIX
                            + 'inicio/solicitudes/%s/' % solicitud.id,
                            '#%s' % solicitud.id))})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
            c = models.Comentario()
            c.solicitud = solicitud
            c.autor = request.user
            c.comentario = request.POST['comentario']
            c.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class SolicitudAgendar(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        else:
            return False

    form_class = forms.SolicitudAgendarForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX
                    + 'inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_agendar.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'object': solicitud,
                       'form': form,
                       'breadcrumbs': self.breadcrumbs.append(
                           (settings.APP_PREFIX
                            + 'inicio/solicitudes/%s/' % solicitud.id,
                            '#%s' % solicitud.id))})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
            sesion = models.Sesion.objects.get(id=request.POST['sesion'])
            solicitud.sesion = sesion
            solicitud.estado = "agendada"
            solicitud.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class SolicitudAnexo(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or self.request.user.is_staff:
            return True
        elif hasattr(self.request.user, 'academico'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.academico.solicitudes()
        elif hasattr(self.request.user, 'estudiante'):
            solicitud = models.Solicitud.objects.get(id=int(self.kwargs['pk']))
            return solicitud in self.request.user.estudiante.solicitudes()
        else:
            return False

    form_class = forms.SolicitudAnexoForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX
                    + 'inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_anexo.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'object': solicitud,
                       'form': form,
                       'breadcrumbs': self.breadcrumbs.append(
                           (settings.APP_PREFIX
                            + 'inicio/solicitudes/%s/' % solicitud.id,
                            '#%s' % solicitud.id))})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            solicitud = models.Solicitud.objects.get(id=int(kwargs['pk']))
            nx = models.Anexo(solicitud=solicitud,
                              autor=request.user,
                              archivo=request.FILES['anexo'])
            nx.save()

            c = models.Comentario()
            c.solicitud = solicitud
            c.autor = request.user
            c.comentario = 'archivo anexado'
            c.save()

            return HttpResponseRedirect(reverse('solicitud_detail',
                                                args=(solicitud.id,)))
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class SolicitudSortableView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            SortableListView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    def get_queryset(self):
        sorted = super(SolicitudSortableView, self).get_queryset()

        if self.args:
            estado = self.args[0]
        else:
            estado = 'todas'

        if self.request.user.is_staff \
           or hasattr(self.request.user, 'asistente'):
            if estado == 'todas':
                return sorted & models.Solicitud.objects.all()
            else:
                return sorted & models.Solicitud.objects.filter(estado=estado)
        elif hasattr(self.request.user, 'academico'):
            return sorted & \
                self.request.user.academico.solicitudes(estado)
        elif hasattr(self.request.user, 'estudiante'):
            return sorted & \
                self.request.user.estudiante.solicitudes(estado)

    allowed_sort_fields = {'resumen': {'default_direction': '',
                                       'verbose_name': 'resumen'},
                           'fecha_creacion': {'default_direction': '-',
                                              'verbose_name':
                                              'Fecha de creación'}}
    default_sort_field = 'fecha_creacion'

    paginate_by = 15

    model = models.Solicitud
