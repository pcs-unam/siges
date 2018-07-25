# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.views import View
from django.views.generic import DetailView
from sortable_listview import SortableListView
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
import datetime
from django.forms.models import model_to_dict
import posgradmin.forms as forms

import posgradmin.models as models

from pprint import pprint


class InicioView(LoginRequiredMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),)

    template_name = 'posgradmin/inicio.html'

    def get(self, request, *args, **kwargs):

        return render(request,
                      self.template_name,
                      {'title': 'Inicio',
                       'breadcrumbs': self.breadcrumbs})


class UserDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = settings.APP_PREFIX + 'accounts/login/'
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

        # may see intimacies?
        u = context['object']

        if (  # by authority
                self.request.user == u
                or self.request.user.is_staff
                or hasattr(self.request.user, 'asistente')):
            see_private = True
        else:
            see_private = False

        context['see_private'] = see_private

        return context


class PerfilDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template_name = "posgradmin/user_detail.html"

    def test_func(self):
        return True

    def get_context_data(self, **kwargs):
        context = super(PerfilDetail, self).get_context_data(**kwargs)
        context['user'] = self.request.user

        # may see intimacies?
        u = context['object']

        if (  # by authority
                self.request.user == u
                or self.request.user.is_staff
                or hasattr(self.request.user, 'asistente')):
            see_private = True
        else:
            see_private = False

        context['see_private'] = see_private

        return context

    def get_object(self):
        return self.request.user


class PerfilRegistroView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    form_class = forms.PerfilModelForm

    breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX + 'inicio/perfil', 'Mi perfil'),
                   (settings.APP_PREFIX + 'inicio/perfil/editar', 'Editar'))

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

            fecha_nacimiento = datetime.date(
                int(request.POST['fecha_nacimiento_year']),
                int(request.POST['fecha_nacimiento_month']),
                int(request.POST['fecha_nacimiento_day']))
            p.fecha_nacimiento = fecha_nacimiento
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
            if 'headshot' in request.FILES:
                p.headshot = request.FILES['headshot']
            p.save()

            return HttpResponseRedirect(reverse('user_detail',
                                                args=(request.user.id,)))
        else:
            return render(request,
                          self.template,
                          {'object': u.perfil,
                           'form': form,
                           'title': 'Editar mi perfil',
                           'breadcrumbs': self.breadcrumbs})


class AcademicoRegistroView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    form_class = forms.AcademicoModelForm

    breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX + 'inicio/academico/registro',
                    'Solicitar registro como Académico'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        if hasattr(request.user, 'academico'):
            a = request.user.academico
            data = model_to_dict(a)
            form = self.form_class(data=data)
        else:
            form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Editar registro Académico',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            if request.POST['entidad'] != '':
                entidad = models.Entidad.objects.get(
                    id=int(request.POST['entidad']))
            else:
                entidad = None

            if hasattr(request.user, 'academico'):
                a = request.user.academico
                a.entidad = entidad
                a.lineas = request.POST[u'lineas']
                a.CVU = request.POST[u'CVU']
                a.nivel_SNI = request.POST[u'nivel_SNI']
                a.nivel_PRIDE = request.POST[u'nivel_PRIDE']
                a.titulo = request.POST[u'titulo']

                if request.POST['tesis_licenciatura'] != "":
                    a.tesis_licenciatura = request.POST['tesis_licenciatura']
                if request.POST['tesis_maestria'] != "":
                    a.tesis_maestria = request.POST['tesis_maestria']
                if request.POST['tesis_doctorado'] != "":
                    a.tesis_doctorado = request.POST['tesis_doctorado']
                if request.POST['tesis_licenciatura_5'] != "":
                    a.tesis_licenciatura_5 = request.POST['tesis_licenciatura_5']
                if request.POST['tesis_maestria_5'] != "":
                    a.tesis_maestria_5 = request.POST['tesis_maestria_5']
                if request.POST['tesis_doctorado_5'] != "":
                    a.tesis_doctorado_5 = request.POST['tesis_doctorado_5']
                if request.POST['participacion_comite_maestria'] != "":
                    a.participacion_comite_maestria = request.POST['participacion_comite_maestria']
                if request.POST['participacion_tutor_maestria'] != "":
                    a.participacion_tutor_maestria = request.POST['participacion_tutor_maestria']
                if request.POST['participacion_comite_doctorado'] != "":
                    a.participacion_comite_doctorado = request.POST['participacion_comite_doctorado']
                if request.POST['participacion_tutor_doctorado'] != "":
                    a.participacion_tutor_doctorado = request.POST['participacion_tutor_doctorado']

                a.tutor_otros_programas = request.POST['tutor_otros_programas']
                a.tutor_principal_otros_programas = request.POST['tutor_principal_otros_programas']

                if request.POST['articulos_internacionales_5'] != "":
                    a.articulos_internacionales_5 = request.POST['articulos_internacionales_5']
                if request.POST['articulos_nacionales_5'] != "":
                    a.articulos_nacionales_5 = request.POST['articulos_nacionales_5']
                if request.POST['articulos_internacionales'] != "":
                    a.articulos_internacionales = request.POST['articulos_internacionales']
                if request.POST['articulos_nacionales'] != "":
                    a.articulos_nacionales = request.POST['articulos_nacionales']
                if request.POST['capitulos'] != "":
                    a.capitulos = request.POST['capitulos']
                if request.POST['capitulos_5'] != "":
                    a.capitulos_5 = request.POST['capitulos_5']
                if request.POST['libros'] != "":
                    a.libros = request.POST['libros']
                if request.POST['libros_5'] != "":
                    a.libros_5 = request.POST['libros_5']

                a.lineas = request.POST['lineas']
                a.palabras_clave = request.POST['palabras_clave']
                a.motivacion = request.POST['motivacion']
                a.proyectos_vigentes = request.POST['proyectos_vigentes']
                if 'disponible_miembro' in request.POST:
                    a.disponible_miembro = True
                else:
                    a.disponible_miembro = False

                if 'disponible_tutor' in request.POST:
                    a.disponible_tutor = True
                else:
                    a.disponible_tutor = False

                a.save()

                return HttpResponseRedirect(reverse('perfil'))

            else:
                s = models.Solicitud()
                s.resumen = 'registrar como académico'
                s.tipo = 'registrar_academico'
                s.solicitante = request.user
                s.save()

                a = models.Academico()
                a.user = request.user
                a.solicitud = s
                a.entidad = entidad
                a.lineas = request.POST[u'lineas']
                a.CVU = request.POST[u'CVU']
                a.nivel_SNI = request.POST[u'nivel_SNI']
                a.nivel_PRIDE = request.POST[u'nivel_PRIDE']
                a.titulo = request.POST[u'titulo']

                if request.POST['tesis_licenciatura'] != "":
                    a.tesis_licenciatura = request.POST['tesis_licenciatura']
                if request.POST['tesis_maestria'] != "":
                    a.tesis_maestria = request.POST['tesis_maestria']
                if request.POST['tesis_doctorado'] != "":
                    a.tesis_doctorado = request.POST['tesis_doctorado']
                if request.POST['tesis_licenciatura_5'] != "":
                    a.tesis_licenciatura_5 = request.POST['tesis_licenciatura_5']
                if request.POST['tesis_maestria_5'] != "":
                    a.tesis_maestria_5 = request.POST['tesis_maestria_5']
                if request.POST['tesis_doctorado_5'] != "":
                    a.tesis_doctorado_5 = request.POST['tesis_doctorado_5']
                if request.POST['participacion_comite_maestria'] != "":
                    a.participacion_comite_maestria = request.POST['participacion_comite_maestria']
                if request.POST['participacion_tutor_maestria'] != "":
                    a.participacion_tutor_maestria = request.POST['participacion_tutor_maestria']
                if request.POST['participacion_comite_doctorado'] != "":
                    a.participacion_comite_doctorado = request.POST['participacion_comite_doctorado']
                if request.POST['participacion_tutor_doctorado'] != "":
                    a.participacion_tutor_doctorado = request.POST['participacion_tutor_doctorado']

                a.tutor_otros_programas = request.POST['tutor_otros_programas']
                a.tutor_principal_otros_programas = request.POST['tutor_principal_otros_programas']

                if request.POST['articulos_internacionales_5'] != "":
                    a.articulos_internacionales_5 = request.POST['articulos_internacionales_5']
                if request.POST['articulos_nacionales_5'] != "":
                    a.articulos_nacionales_5 = request.POST['articulos_nacionales_5']
                if request.POST['articulos_internacionales'] != "":
                    a.articulos_internacionales = request.POST['articulos_internacionales']
                if request.POST['articulos_nacionales'] != "":
                    a.articulos_nacionales = request.POST['articulos_nacionales']
                if request.POST['capitulos'] != "":
                    a.capitulos = request.POST['capitulos']
                if request.POST['capitulos_5'] != "":
                    a.capitulos_5 = request.POST['capitulos_5']
                if request.POST['libros'] != "":
                    a.libros = request.POST['libros']
                if request.POST['libros_5'] != "":
                    a.libros_5 = request.POST['libros_5']


                a.lineas = request.POST['lineas']
                a.palabras_clave = request.POST['palabras_clave']
                a.motivacion = request.POST['motivacion']
                a.proyectos_vigentes = request.POST['proyectos_vigentes']
                a.disponible_miembro = request.POST['disponible_miembro']
                a.disponible_tutor = request.POST['disponible_tutor']
                a.save()

                return HttpResponseRedirect(reverse('solicitud_detail',
                                                    args=(s.id,)))

        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Solicitar registro como Académico',
                           'breadcrumbs': self.breadcrumbs})


class GradoAcademicoAgregar(LoginRequiredMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    form_class = forms.GradoAcademicoModelForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX + 'inicio/perfil/', 'Mi perfil'),
                   (settings.APP_PREFIX
                    + 'inicio/perfil/agregar-grado',
                    'Agregar Grado Académico')]

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

            return HttpResponseRedirect(reverse('perfil'))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Grado Académico',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class GradoAcademicoEliminar(LoginRequiredMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def get(self, request, *args, **kwargs):
        g = models.GradoAcademico.objects.get(id=int(kwargs['pk']))
        g.delete()
        return HttpResponseRedirect(reverse('perfil'))


class AdscripcionAgregar(LoginRequiredMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    form_class = forms.AdscripcionModelForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX + 'inicio/perfil/', 'Mi perfil'),
                   (settings.APP_PREFIX + 'inicio/perfil/agregar-adscrpcion',
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
            a = models.Adscripcion(user=request.user,
                                   institucion=ins,
                                   cargo=request.POST['cargo'])
            a.save()

            return HttpResponseRedirect(reverse('perfil'))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Adscripción',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class AdscripcionEliminar(LoginRequiredMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    def get(self, request, *args, **kwargs):
        a = models.Adscripcion.objects.get(id=int(kwargs['pk']))
        a.delete()
        return HttpResponseRedirect(reverse('perfil'))


class InstitucionAgregarView(LoginRequiredMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'

    form_class = forms.InstitucionModelForm

    breadcrumbs = [(settings.APP_PREFIX + 'inicio/', 'Inicio'),
                   (settings.APP_PREFIX +
                    'institucion/agregar', 'Agregar Institución')]

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
            i = models.Institucion(
                nombre=request.POST['nombre'],
                pais=request.POST['pais'],
                estado=request.POST['estado'],
                suborganizacion=request.POST['suborganizacion'],
                dependencia_unam=True
                if request.POST['dependencia_unam'] == 'on' else False,
                entidad_PCS=True
                if request.POST['entidad_PCS'] == 'on' else False)
            i.save()

            return HttpResponseRedirect(reverse('editar_perfil'))
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Institución',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class EstudianteSortableView(LoginRequiredMixin,
                             UserPassesTestMixin,
                             SortableListView):

    login_url = settings.APP_PREFIX + 'accounts/login/'

    def test_func(self):
        return True

    def get_queryset(self):

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
    login_url = settings.APP_PREFIX + 'accounts/login/'

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
    login_url = settings.APP_PREFIX + 'accounts/login/'



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
