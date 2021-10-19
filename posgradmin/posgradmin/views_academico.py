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
from pdfrw import PdfReader, PdfWriter, PageMerge
from django.template.loader import render_to_string
from sh import pandoc, mkdir
from tempfile import NamedTemporaryFile
import datetime
from django.utils.text import slugify


from .settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL



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



class ProponerAsignatura(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/proponer_asignatura.html'
    form_class = forms.AsignaturaModelForm

    def test_func(self):
        if auth.is_academico(self.request.user):
            if self.request.user.academico.acreditacion in ['D', 'M', 'P',
                                                            'candidato profesor']:
                return True
        return False


    def get(self, request, *args, **kwargs):

        form = self.form_class(initial={'academicos': [request.user.academico, ]})

        breadcrumbs = ((settings.APP_PREFIX + 'inicio/', 'Inicio'),
                       ('', 'Proponer Asignatura')
                      )

        return render(request,
                      self.template,
                      {
                          'title': 'Proponer Asignatura',
                          'breadcrumbs': breadcrumbs,
                          'form': form
                       })


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            a = models.Asignatura(
                asignatura=request.POST['asignatura'],
                tipo='Optativa',
                estado='propuesta',
                programa=request.FILES['programa'])
            a.save()
            return HttpResponseRedirect(reverse('inicio'))
        else:
            print(form.errors)



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



class CursoConstancia(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/curso_constancia.html'
    form_class = forms.CursoConstancia

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
                          'title': 'Emitir constancia de participación',
                          'breadcrumbs': breadcrumbs,
                          'convocatoria': curso.convocatoria,
                          'asignatura': curso.asignatura,
                          'form': form
                       })


    def post(self, request, *args, **kwargs):
        curso = models.Curso.objects.get(pk=int(kwargs['pk']))

        profesor_invitado = request.POST['profesor_invitado']

        fecha_participacion = datetime.date(int(request.POST['fecha_de_participación_year']),
                                            int(request.POST['fecha_de_participación_month']),
                                            int(request.POST['fecha_de_participación_day']))

        with NamedTemporaryFile(mode='r+', encoding='utf-8') as carta_md:
            carta_md.write(
                render_to_string('posgradmin/constancia_curso.md',
                                 {'fecha': datetime.date.today(),
                                  'profesor_invitado': profesor_invitado,
                                  'tema': request.POST['tema'],
                                  'curso': curso,
                                  'fecha_participacion': fecha_participacion,
                                  'profesor': request.user.get_full_name() }))
            carta_md.seek(0)

            outdir = '%s/perfil-academico/%s/' % (MEDIA_ROOT,
                                                  request.user.academico.id)

            tmpname = 'cursoplain_%s_%s.pdf' % (curso.id,
                                                slugify(profesor_invitado)
            )

            final_name = tmpname.replace('cursoplain', 'constancia_curso')

            mkdir("-p", outdir)
            pandoc(carta_md.name, output=outdir + tmpname)
            C = PdfReader(outdir + tmpname)
            M = PdfReader(BASE_DIR + '/docs/membrete_pcs.pdf')
            w = PdfWriter()
            merger = PageMerge(M.pages[0])
            merger.add(C.pages[0]).render()

            w.write(outdir + final_name, M)

        return HttpResponseRedirect(MEDIA_URL+"perfil-academico/%s/%s" % (request.user.academico.id, final_name))




class CursoConstanciaEstudiante(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.APP_PREFIX + 'accounts/login/'
    template = 'posgradmin/curso_constancia.html'
    form_class = forms.CursoConstanciaEstudiante

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
                          'title': 'Emitir constancia para estudiante',
                          'breadcrumbs': breadcrumbs,
                          'convocatoria': curso.convocatoria,
                          'asignatura': curso.asignatura,
                          'form': form
                       })


    def post(self, request, *args, **kwargs):
        curso = models.Curso.objects.get(pk=int(kwargs['pk']))
        
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            estudiante_invitado = request.POST['estudiante_invitado']
            calificacion = request.POST['calificacion']
        
            with NamedTemporaryFile(mode='r+', encoding='utf-8') as carta_md:
                carta_md.write(
                    render_to_string('posgradmin/constancia_curso_estudiante.md',
                                     {'fecha': datetime.date.today(),
                                      'estudiante_invitado': estudiante_invitado,
                                      'calificacion': calificacion,
                                      'curso': curso,
                                      'profesor': request.user.get_full_name() }))
                carta_md.seek(0)

                outdir = '%s/perfil-academico/%s/' % (MEDIA_ROOT,
                                                      request.user.academico.id)

                tmpname = 'cursoplain_%s_%s.pdf' % (curso.id,
                                                    slugify(estudiante_invitado)
                )

                final_name = tmpname.replace('cursoplain', 'constancia_curso')

                mkdir("-p", outdir)
                pandoc(carta_md.name, output=outdir + tmpname)
                C = PdfReader(outdir + tmpname)
                M = PdfReader(BASE_DIR + '/docs/membrete_pcs.pdf')
                w = PdfWriter()
                merger = PageMerge(M.pages[0])
                merger.add(C.pages[0]).render()

                w.write(outdir + final_name, M)

            return HttpResponseRedirect(
                MEDIA_URL + "perfil-academico/%s/%s" % (request.user.academico.id,
                                                        final_name))
        else:
            return render(request,
                          self.template,
                          {
                              'title': 'Emitir constancia para estudiante',
                              'breadcrumbs': breadcrumbs,
                              'convocatoria': curso.convocatoria,
                              'asignatura': curso.asignatura,
                              'form': form
                          })
            




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
        return self.request.user.academico.curso_set.all()


    def get_context_data(self, **kwargs):
        ctxt = super(MisCursos, self).get_context_data(**kwargs)
        ctxt['MEDIA_URL'] = MEDIA_URL
        return ctxt
