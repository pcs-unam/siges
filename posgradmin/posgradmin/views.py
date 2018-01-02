# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.views import View
from django.views.generic import DetailView
from sortable_listview import SortableListView
from django.shortcuts import render, HttpResponseRedirect

from django.forms.models import model_to_dict
import posgradmin.forms as forms

import posgradmin.models as models

from pprint import pprint


class InicioView(LoginRequiredMixin, View):

    breadcrumbs = (('/inicio/', 'Inicio'),)

    template_name = 'posgradmin/inicio.html'

    def get(self, request, *args, **kwargs):

        return render(request,
                      self.template_name,
                      {'title': 'Inicio',
                       'breadcrumbs': self.breadcrumbs})


class UserDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = models.User
    template_name = "posgradmin/user_detail.html"

    def test_func(self):
        if hasattr(self.request.user, 'asistente') \
           or hasattr(self.request.user, 'estudiante') \
           or hasattr(self.request.user, 'academico') \
           or self.request.user.is_staff:
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class PerfilDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = "posgradmin/user_detail.html"

    def test_func(self):
        return True

    def get_object(self):
        return self.request.user


class PerfilRegistroView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return True

    form_class = forms.PerfilModelForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/perfil', 'Mi perfil'),
                   ('/inicio/perfil/editar', 'Editar'))

    template = 'posgradmin/perfil_editar.html'

    def get(self, request, *args, **kwargs):
        try:
            perfil = request.user.perfil
            data = model_to_dict(perfil)
            data['fecha_nacimiento'] = data['fecha_nacimiento'].isoformat()
            data['nombre'] = request.user.first_name
            data['apellidos'] = request.user.last_name
            form = self.form_class(data=data)
        except:
            data = {'nombre': request.user.first_name,
                    'apellidos': request.user.last_name}
            form = self.form_class(data=data)
            return render(request,
                          self.template,
                          {'form': form,
                           'title': 'Editar mi perfil',
                           'breadcrumbs': self.breadcrumbs})

        return render(request,
                      self.template,
                      {'object': perfil,
                       'form': form,
                       'title': 'Editar mi perfil',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            u = request.user
            u.first_name = request.POST['nombre']
            u.last_name = request.POST['apellidos']
            u.save()
            try:
                p = request.user.perfil
            except:
                p = models.Perfil()

            p.user = request.user
            p.fecha_nacimiento = request.POST['fecha_nacimiento']
            p.genero = request.POST['genero']
            p.nacionalidad = request.POST['nacionalidad']
            p.curp = request.POST['curp']
            p.rfc = request.POST['rfc']
            p.telefono = request.POST['telefono']
            p.telefono_movil = request.POST['telefono_movil']
            p.email2 = request.POST['email2']
            p.website = request.POST['website']
            p.direccion1 = request.POST['direccion1']
            p.direccion2 = request.POST['direccion2']
            p.codigo_postal = request.POST['codigo_postal']
            p.save()

            return HttpResponseRedirect('/inicio/usuario/%s' % request.user.id)
        else:
            return render(request,
                          self.template,
                          {'object': u.perfil,
                           'form': form,
                           'title': 'Editar mi perfil',
                           'breadcrumbs': self.breadcrumbs})


class AcademicoRegistroView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return True

    form_class = forms.AcademicoModelForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/academico/registro',
                    'Solicitar registro como Académico'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Solicitar registro como Académico',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            s = models.Solicitud()
            s.resumen = 'registrar como académico'
            s.tipo = 'registrar_academico'
            s.solicitante = request.user
            s.save()

            a, created = models.Academico.objects.get_or_create(
                user=request.user)
            a.solicitud = s
            a.save()

            return HttpResponseRedirect('/inicio/solicitudes/%s/'
                                        % s.id)

        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Solicitar registro como Académico',
                           'breadcrumbs': self.breadcrumbs})


class GradoAcademicoAgregar(LoginRequiredMixin, View):

    form_class = forms.GradoAcademicoModelForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/inicio/perfil/', 'Mi perfil'),
                   ('/inicio/perfil/agregar-grado', 'Agregar Grado Académico')]

    template_name = 'posgradmin/grado_academico_agregar.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request,
                      self.template_name,
                      {'title': 'Agregar Grado Académico',
                       'form': form,
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            ins = models.Institucion.objects.get(
                id=int(request.POST['institucion']))
            g = models.GradoAcademico(
                user=request.user,
                nivel=request.POST['nivel'],
                grado_obtenido=request.POST['grado_obtenido'],
                institucion=ins,
                facultad=request.POST['facultad'],
                fecha_obtencion=request.POST['fecha_obtencion'],
                promedio=request.POST['promedio'],
                documento=request.FILES['documento'])
            g.save()

            return HttpResponseRedirect("/inicio/perfil/")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Grado Académico',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class GradoAcademicoEliminar(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        g = models.GradoAcademico.objects.get(id=int(kwargs['pk']))
        g.delete()
        return HttpResponseRedirect("/inicio/perfil/")


class EmpleoAgregar(LoginRequiredMixin, View):

    form_class = forms.EmpleoModelForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/inicio/perfil/', 'Mi perfil'),
                   ('/inicio/perfil/agregar-adscrpcion',
                    'Agregar Adscripción')]

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request,
                      self.template_name,
                      {'title': 'Agregar Adscripcion',
                       'form': form,
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            ins = models.Institucion.objects.get(
                id=int(request.POST['institucion']))
            a = models.Empleo(user=request.user,
                              institucion=ins,
                              cargo=request.POST['cargo'])
            a.save()

            return HttpResponseRedirect("/inicio/perfil/")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Adscripción',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class EmpleoEliminar(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        a = models.Empleo.objects.get(id=int(kwargs['pk']))
        a.delete()
        return HttpResponseRedirect("/inicio/perfil/")


class InstitucionAgregarView(LoginRequiredMixin, View):

    form_class = forms.InstitucionModelForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/institucion/agregar', 'Agregar Institución')]

    template_name = 'posgradmin/institucion_agregar.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request,
                      self.template_name,
                      {'title': 'Agregar Institución',
                       'form': form,
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            i = models.Institucion(nombre=request.POST['nombre'],
                                   pais=request.POST['pais'],
                                   estado=request.POST['estado'])
            i.save()

            return HttpResponseRedirect("/inicio/perfil/editar")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Institución',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class EstudianteSortableView(LoginRequiredMixin,
                             UserPassesTestMixin,
                             SortableListView):

    def test_func(self):
        return True

    def get_queryset(self):
        #pprint(self.get_querystring())
        #print search
        print self.request.encoding
        self.request.GET.encoding = 'utf-8'
        search = self.request.GET.get('search', None)
        qs = super(EstudianteSortableView, self).get_queryset()

        if search:
            search = search.encode('utf-8')
            sorted = qs.filter(Q(cuenta__icontains=search) |
                               Q(user__first_name__icontains=search) |
                               Q(user__last_name__icontains=search))
        else:
            sorted = qs
        return sorted

    allowed_sort_fields = {'user': {'default_direction': '',
                                    'verbose_name': 'nombre'},
                           'estado': {'default_direction': '-',
                                      'verbose_name': 'estado'},
                           'ingreso': {'default_direction': '-',
                                       'verbose_name': 'año de ingreso'}}
    default_sort_field = 'user'

    paginate_by = 15

    model = models.Estudiante


class AcademicoSortableView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            SortableListView):

    def test_func(self):
        return True

    # def get_queryset(self):
    #     sorted = super(EstudianteSortableView, self).get_queryset()

    allowed_sort_fields = {'user': {'default_direction': '',
                                    'verbose_name': 'nombre'},
                           'entidad': {'default_direction': '-',
                                       'verbose_name': 'entidad'},
                           'acreditacion': {'default_direction': '-',
                                            'verbose_name':
                                            'acreditación'}}
    default_sort_field = 'user'

    paginate_by = 15

    model = models.Academico


class CatedraSortableView(LoginRequiredMixin,
                          UserPassesTestMixin,
                          SortableListView):

    def test_func(self):
        return True

    def get_queryset(self):
        sorted = super(CatedraSortableView, self).get_queryset()
        return sorted

    allowed_sort_fields = {'profesor': {'default_direction': '',
                                        'verbose_name': 'profesor'},
                           'curso': {'default_direction': '-',
                                     'verbose_name': 'curso'},
                           'semestre': {'default_direction': '-',
                                        'verbose_name': 'semestre'},
                           'year': {'default_direction': '-',
                                    'verbose_name': 'año'}}
    default_sort_field = 'curso'

    paginate_by = 15

    model = models.Catedra
