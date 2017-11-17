# coding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, ListView
from django.views import View
from django.shortcuts import render, HttpResponseRedirect
from django.forms.models import model_to_dict
from sortable_listview import SortableListView
from posgradmin.models import Solicitud, Anexo, Perfil, Estudiante, \
    Academico, CampoConocimiento, Comentario, GradoAcademico, \
    Institucion, Comite, Proyecto, Catedra, Adscripcion, Dictamen, Curso, \
    Sesion
from posgradmin.forms import SolicitudForm, PerfilModelForm, \
    AcademicoModelForm, EstudianteAutoregistroForm, SolicitudCommentForm, \
    SolicitudAnexoForm, GradoAcademicoModelForm, InstitucionModelForm, \
    ComiteTutoralModelForm, ProyectoModelForm, CatedraModelForm, \
    AdscripcionModelForm, SolicitudDictamenForm, EstudianteCargarForm
from settings import solicitudes_profesoriles,\
    solicitudes_tutoriles, solicitudes_estudiantiles, solicitud_otro
from posgradmin import workflows
import etl

from pprint import pprint


class InicioView(View):

    breadcrumbs = (('/inicio/', 'Inicio'),)

    template_name = 'posgradmin/inicio.html'

    def get(self, request, *args, **kwargs):

        return render(request,
                      self.template_name,
                      {'title': 'Inicio',
                       'breadcrumbs': self.breadcrumbs})


class SolicitudCambiarEstado(View):

    def get(self, request, *args, **kwargs):
        sid = int(kwargs['pk'])
        s = Solicitud.objects.get(id=sid)
        s.estado = kwargs['estado']
        s.save()
        return HttpResponseRedirect("/inicio/solicitudes/%s" % sid)


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
            elif a.acreditado():
                choices += solicitudes_profesoriles
                choices += (("solicitar_registro_como_tutor",
                             "Solicitar Registro como Tutor"),)

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

    def get_context_data(self, **kwargs):
        context = super(SolicitudDetail, self).get_context_data(**kwargs)
        context['dictaminable'] = context[
            'object'].dictaminable(self.request.user)
        print context['object'].dictaminable(self.request.user)
        context[
            'cancelable'] = context['object'].cancelable(self.request.user)
        return context


class SolicitudDictaminar(View):

    form_class = SolicitudDictamenForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/inicio/solicitudes/', 'Solicitudes')]

    template_name = 'posgradmin/solicitud_comment.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class()
        solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
        # envia todo a la plantilla
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
            if 'denegar' in request.POST:
                if solicitud.tipo == 'registrar_catedra':
                    ct = solicitud.catedra
                    ct.delete()
                d = Dictamen(resolucion='denegada',
                             solicitud=solicitud,
                             autor=request.user)
                c.comentario = '## Dictamen: solicitud denegada\n\n'
            elif 'conceder' in request.POST:
                if solicitud.tipo == 'registrar_catedra':
                    ct = solicitud.catedra
                    ct.profesor = solicitud.solicitante.academico
                    ct.save()
                d = Dictamen(resolucion='concedida',
                             solicitud=solicitud,
                             autor=request.user)
                c.comentario = '## Dictamen: solicitud concedida\n\n'
            d.save()

            c.comentario += request.POST['comentario']
            c.save()

            if request.user.is_staff or hasattr(request.user, 'asistente'):
                solicitud.estado = 'atendida'
            solicitud.save()

            return HttpResponseRedirect("/inicio/solicitudes/%s/"
                                        % solicitud.id)
        else:
            return render(request,
                          self.template_name,
                          {'object': solicitud,
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


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
        else:
            estado = 'todas'

        if self.request.user.is_staff \
           or hasattr(self.request.user, 'asistente'):
            if estado == 'todas':
                return sorted & Solicitud.objects.all()
            else:
                return sorted & Solicitud.objects.filter(estado=estado)
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

    model = Solicitud


class PerfilDetail(DetailView):
    def get_object(self):
        return self.request.user.perfil


class PerfilRegistroView(View):

    form_class = PerfilModelForm

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
                          {'object': u.perfil,
                           'form': form,
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
            e.save()

            s = Solicitud(
                resumen='Cambio de título y/o campo de conocimiento de proyecto',
                tipo='cambio_proyecto',
                solicitante=request.user)
            s.save()

            p = Proyecto(
                estudiante=e,
                solicitud=s,
                campo_conocimiento=CampoConocimiento.objects.get(
                    id=int(request.POST['campo_conocimiento'])),
                nombre=request.POST['proyecto'])
            p.save()

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
            s = Solicitud()
            s.resumen = 'registrar como académico'
            s.tipo = 'registrar_academico'
            s.solicitante = request.user
            s.save()

            a = Academico()
            a.user = request.user
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


class AdscripcionAgregar(View):

    form_class = AdscripcionModelForm

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
            ins = Institucion.objects.get(id=int(request.POST['institucion']))
            a = Adscripcion(academico=request.user.academico,
                            institucion=ins,
                            nombramiento=request.POST['nombramiento'],
                            telefono=request.POST['telefono'],
                            numero_trabajador=request.POST[
                                'numero_trabajador'])
            a.save()

            return HttpResponseRedirect("/inicio/perfil/")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Adscripción',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class AdscripcionEliminar(View):

    def get(self, request, *args, **kwargs):
        a = Adscripcion.objects.get(id=int(kwargs['pk']))
        a.delete()
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

            return HttpResponseRedirect("/inicio/perfil/editar")
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Agregar Institución',
                           'form': form,
                           'breadcrumbs': self.breadcrumbs})


class ComiteElegirView(View):

    form_class = ComiteTutoralModelForm

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
        solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
        form = self.form_class(request.POST)
        if form.is_valid():
            presidente = Academico.objects.get(
                id=int(request.POST['presidente']))
            secretario = Academico.objects.get(
                id=int(request.POST['secretario']))
            vocal = Academico.objects.get(
                id=int(request.POST['vocal']))
            comite = Comite(estudiante=request.user.estudiante,
                            solicitud=Solicitud.objects.get(
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


class ComiteTutoralElegirView(ComiteElegirView):
    tipo = 'tutoral'
    title = 'Elegir Comité Tutoral'

    def get_breadcrumbs(self, pk):
        solicitud = Solicitud.objects.get(id=pk)
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                ('/inicio/solicitudes/%s/elegir-comite-tutoral'
                 % solicitud.id, 'Elegir Comité Tutoral')]


class JuradoCandidaturaElegirView(ComiteElegirView):
    tipo = 'candidatura'
    title = 'Elegir Jurado para Candidatura'

    def get_breadcrumbs(self, pk):
        solicitud = Solicitud.objects.get(id=pk)
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                ('/inicio/solicitudes/%s/elegir-jurado-candidatura'
                 % solicitud.id, 'Elegir Jurado para Candidatura')]


class JuradoGradoElegirView(ComiteElegirView):
    tipo = 'grado'
    title = 'Elegir Jurado para Examen de Grado'

    def get_breadcrumbs(self, pk):
        solicitud = Solicitud.objects.get(id=pk)
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % solicitud.id,
                 '#%s' % solicitud.id),
                ('/inicio/solicitudes/%s/elegir-jurado-grado'
                 % solicitud.id, 'Elegir Jurado para Examen de Grado')]


class CambiarProyectoView(View):
    form_class = ProyectoModelForm
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
        solicitud = Solicitud.objects.get(id=int(kwargs['pk']))
        if form.is_valid():
            p = Proyecto(nombre=request.POST['nombre'],
                         campo_conocimiento=CampoConocimiento.objects.get(
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


class MisCatedrasView(ListView):
    model = Catedra

    def get_queryset(self):
        new_context = Catedra.objects.filter(
            profesor=self.request.user.academico
        )
        return new_context


class SesionesView(SortableListView):
    allowed_sort_fields = {'fecha': {'default_direction': '-',
                                     'verbose_name': 'fecha'}}
    default_sort_field = 'fecha'    
    paginate_by = 15    
    model = Sesion

    
class CatedraRegistrar(View):

    form_class = CatedraModelForm

    def get_breadcrumbs(self, pk):
        return [('/inicio/', 'Inicio'),
                ('/inicio/solicitudes/', 'Solicitudes'),
                ('/inicio/solicitudes/%s/' % pk,
                 '#%s' % pk),
                ('/inicio/solicitudes/%s/registrar-catedra'
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
        s = Solicitud.objects.get(id=sid)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            curso = Curso.objects.get(
                id=int(request.POST['curso']))
            c = Catedra(curso=curso,
                        year=request.POST['year'],
                        semestre=request.POST['semestre'],
                        solicitud=s)
            c.save()
            pprint(request.POST)

            return HttpResponseRedirect("/inicio/solicitudes/%s" % s.id)
        else:
            return render(request,
                          self.template_name,
                          {'title': 'Registrar Curso',
                           'form': form,
                           'breadcrumbs': self.get_breadcrumbs(kwargs['pk'])})


class EstudianteSortableView(SortableListView):

    # def get_queryset(self):
    #     sorted = super(EstudianteSortableView, self).get_queryset()

    allowed_sort_fields = {'user': {'default_direction': '',
                                    'verbose_name': 'nombre'},
                           'estado': {'default_direction': '-',
                                      'verbose_name': 'estado'},
                           'ingreso': {'default_direction': '-',
                                       'verbose_name': 'año de ingreso'}}
    default_sort_field = 'user'

    paginate_by = 15

    model = Estudiante


class AcademicoSortableView(SortableListView):

    # def get_queryset(self):
    #     sorted = super(EstudianteSortableView, self).get_queryset()

    allowed_sort_fields = {'user': {'default_direction': '',
                                    'verbose_name': 'nombre'},
                           'entidad': {'default_direction': '-',
                                       'verbose_name': 'entidad'},
                           'fecha_acreditacion': {'default_direction': '-',
                                                  'verbose_name':
                                                  'fecha de acreditación'}}
    default_sort_field = 'user'

    paginate_by = 15

    model = Academico


class CatedraSortableView(SortableListView):

    # def get_queryset(self):
    #     sorted = super(EstudianteSortableView, self).get_queryset()

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

    model = Catedra


class EstudianteCargar(View):

    form_class = EstudianteCargarForm

    breadcrumbs = [('/inicio/', 'Inicio'),
                   ('/inicio/estudiantes/', 'Estudiantes')]

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
                return HttpResponseRedirect("/inicio/estudiantes")
        else:
            return render(request,
                          self.template_name,
                          {'form': form,
                           'breadcrumbs': self.breadcrumbs})
