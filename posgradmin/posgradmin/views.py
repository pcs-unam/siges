# coding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from django.forms.models import model_to_dict
from sortable_listview import SortableListView
from posgradmin.models import Solicitud, Anexo, Perfil, Estudiante, \
    Academico, CampoConocimiento, Comentario, GradoAcademico, \
    Institucion
from posgradmin.forms import SolicitudForm, PerfilModelForm, \
    AcademicoModelForm, EstudianteAutoregistroForm, SolicitudCommentForm, \
    SolicitudAnexoForm, GradoAcademicoModelForm, InstitucionModelForm, \
    ComiteTutoralModelForm
from settings import solicitudes_profesoriles,\
    solicitudes_tutoriles, solicitudes_estudiantiles, solicitud_otro
from posgradmin import workflows


from pprint import pprint


class InicioView(View):

    breadcrumbs = (('/inicio/', 'Inicio'),)

    template_name = 'posgradmin/inicio.html'

    def get(self, request, *args, **kwargs):

        return render(request,
                      self.template_name,
                      {'title': 'Inicio',
                       'breadcrumbs': self.breadcrumbs})


class SolicitudNuevaView(View):

    form_class = SolicitudForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/solicitudes/', 'Solicitudes'),
                   ('/inicio/solicitudes/nueva', 'Nueva'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):

        choices = []
        # opciones de academico
        try:
            a = request.user.academico
            if a.tutor:
                choices += solicitudes_tutoriles
            else:
                choices += (("solicitar_registro_como_tutor",
                             "Solicitar Registro como Tutor"),)

            if a.profesor:
                choices += solicitudes_profesoriles

        except ObjectDoesNotExist:
            pass
        # opciones de estudiante
        try:
            request.user.estudiante
            choices += solicitudes_estudiantiles
        except ObjectDoesNotExist:
            pass

        choices += solicitud_otro

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
            s = Solicitud()
            s.resumen = request.POST['resumen']
            s.tipo = request.POST['tipo']
            s.solicitante = request.user
            s.descripcion = request.POST['descripcion']
            s.save()

            if 'anexo' in request.FILES:
                nx = Anexo(solicitud=s,
                           autor=request.user,
                           archivo=request.FILES['anexo'])
                nx.save()

            next = workflows.solicitud.get(s.tipo,
                                           '/inicio/solicitudes/%s')
            return HttpResponseRedirect(next % s.id)
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Solicitud nueva',
                           'breadcrumbs': self.breadcrumbs})


class SolicitudDetail(DetailView):
    model = Solicitud


class SolicitudComment(View):

    form_class = SolicitudCommentForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_comment.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'object': solicitud,
                       'form': form,
                       'breadcrumbs': self.breadcrumbs.append(
                           ('/inicio/solicitudes/%s/' % solicitud.id,
                            '#%s' % solicitud.id))})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
            c = Comentario()
            c.solicitud = solicitud
            c.autor = request.user
            c.comentario = request.POST['comentario']
            c.save()

            return HttpResponseRedirect("/inicio/solicitudes/%s/"
                                        % solicitud.id)
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class SolicitudAnexo(View):

    form_class = SolicitudAnexoForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_anexo.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla etc
        return render(request,
                      self.template_name,
                      {'object': solicitud,
                       'form': form,
                       'breadcrumbs': self.breadcrumbs.append(
                           ('/inicio/solicitudes/%s/' % solicitud.id,
                            '#%s' % solicitud.id))})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
            nx = Anexo(solicitud=solicitud,
                       autor=request.user,
                       archivo=request.FILES['anexo'])
            nx.save()

            c = Comentario()
            c.solicitud = solicitud
            c.autor = request.user
            c.comentario = 'archivo anexado'
            c.save()

            return HttpResponseRedirect("/inicio/solicitudes/%s/"
                                        % solicitud.id)
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class SolicitudSortableView(SortableListView):

    def get_queryset(self):
        sorted = super(SolicitudSortableView, self).get_queryset()
        if self.args:
            estado = self.args[0]
            if estado == 'todas':
                return sorted & self.request.user.estudiante.solicitudes()
            else:
                return sorted & \
                    self.request.user.estudiante.solicitudes(estado)
        else:
            return sorted & self.request.user.estudiante.solicitudes()

    allowed_sort_fields = {'resumen': {'default_direction': '',
                                       'verbose_name': 'resumen'},
                           'fecha_creacion': {'default_direction': '-',
                                              'verbose_name': 'Fecha de publicación'}}
    default_sort_field = 'fecha_creacion'
    paginate_by = 5

    model = Solicitud


class PerfilDetail(DetailView):
    def get_object(self):
        return self.request.user.perfil


class PerfilRegistroView(View):

    form_class = PerfilModelForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/perfil', 'Mi perfil'),
                   ('/inicio/perfil/editar', 'Editar'))

    template = 'posgradmin/try.html'

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
                p = Perfil()

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

            return HttpResponseRedirect('/inicio/')
        else:
            return render(request,
                          self.template,
                          {'form': form,
                           'title': 'Editar mi perfil',
                           'breadcrumbs': self.breadcrumbs})


class EstudianteRegistroView(View):

    form_class = EstudianteAutoregistroForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/estudiante/registro', 'Registro como estudiante'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Registrarse como Estudiante',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            e = Estudiante()
            e.user = request.user
            e.estado = 'aspirante'
            campo = CampoConocimiento.objects.get(
                id=int(request.POST['campo_conocimiento']))
            e.campo_conocimiento = campo
            e.nombre_proyecto = request.POST['proyecto']
            e.save()

            return HttpResponseRedirect('/inicio/')
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Registrarse como Estudiante',
                           'breadcrumbs': self.breadcrumbs})


class AcademicoRegistroView(View):

    form_class = AcademicoModelForm

    breadcrumbs = (('/inicio/', 'Inicio'),
                   ('/inicio/academico/registro', 'Registrarse como Académico'))

    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request,
                      self.template_name,
                      {'form': form,
                       'title': 'Registrarse como Académico',
                       'breadcrumbs': self.breadcrumbs})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            a = Academico()
            a.user = request.user
            a.save()

            return HttpResponseRedirect('/inicio/')
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'title': 'Registrarse como Académico',
                           'breadcrumbs': self.breadcrumbs})


class GradoAcademicoAgregar(View):

    form_class = GradoAcademicoModelForm

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
            ins = Institucion.objects.get(id=int(request.POST['institucion']))
            g = GradoAcademico(user=request.user,
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


class GradoAcademicoEliminar(View):

    def get(self, request, *args, **kwargs):
        g = GradoAcademico.objects.get(id=int(kwargs['pk']))
        g.delete()
        return HttpResponseRedirect("/inicio/perfil/")        


class InstitucionAgregarView(View):

    form_class = InstitucionModelForm

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
            i = Institucion(nombre=request.POST['nombre'],
                            pais=request.POST['pais'],
                            estado=request.POST['estado'])
            i.save()

            return HttpResponseRedirect("/inicio/perfil/agregar-grado")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Institución',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class ComiteTutoralElegirView(View):

    form_class = ComiteTutoralModelForm
    

    template_name = 'posgradmin/institucion_agregar.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
        breadcrumbs = [('/inicio/', 'Inicio'),
                       ('/inicio/solicitudes/', 'Solicitudes'),
                       ('/inicio/solicitudes/%s/' % solicitud.id,
                        '#%s' % solicitud.id),
                       ('/inicio/solicitudes/%s/elegir-comite-tutoral'
                        % solicitud.id,
                        'Elegir Comité Tutoral')]
        return render(request,
                      self.template_name,
                      {'title': 'Elegir Comité Tutoral',
                       'form': form,
                       'breadcrumbs': breadcrumbs})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # i = Institucion(nombre=request.POST['nombre'],
            #                 pais=request.POST['pais'],
            #                 estado=request.POST['estado'])
            # i.save()

            return HttpResponseRedirect("/inicio/perfil/agregar-grado")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Elegir Comité Tutoral',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})
