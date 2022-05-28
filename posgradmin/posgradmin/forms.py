# coding: utf-8
from datetime import datetime
from django import forms
from django.forms.widgets import FileInput
#from django.forms import extras
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import PrependedText, AppendedText, FormActions
from django.utils.safestring import mark_safe
from posgradmin.models import Perfil, Estudiante, Academico, \
    CampoConocimiento, GradoAcademico, Institucion, \
    Proyecto, Curso, Sesion, Adscripcion, Asignatura, ConvocatoriaCurso
from django.conf import settings
from dal import autocomplete
from pprint import pprint


class TogglePerfilEditarForm(forms.Form):
    toggle = forms.BooleanField(required=False,
                                label='Perfiles editables')
    helper = FormHelper()
    helper.layout = Layout(
        Field('toggle'),
        FormActions(
            Submit('OK', 'OK', css_class="btn-primary")
        )
    )



class AcademicoInvitarForm(forms.Form):

    CHOICES=[('candidato','invitar tutores'),
             ('candidato profesor','invitar profesores')]

    lista = forms.FileField(required=True)

    tutor_o_profesor = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    helper = FormHelper()
    helper.layout = Layout(
        Field('tutor_o_profesor'),
        Field('lista'),
        FormActions(
            Submit('subir', 'Crear candidatos', css_class="btn-primary")
        )
    )


class SolicitudForm(forms.Form):

    tipo = forms.ChoiceField(
        choices=(),
        widget=forms.RadioSelect,
        initial='otro',
    )

    resumen = forms.CharField()

    descripcion = forms.CharField(
        widget=forms.Textarea(),
        required=False
    )

    anexo = forms.FileField(required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('tipo',
              onfocus=mark_safe("$('#id_resumen').val(this.value);")),

        Field('resumen', size=70),

        Field('descripcion', rows="3", cols="70", css_class='input-xlarge'),
        Field('anexo'),

        FormActions(
            Submit('someter', 'Someter Solicitud', css_class="btn-primary")
        )
    )


class AsignaturaModelForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        exclude = ['estado', 'tipo', 'campos_de_conocimiento', 'clave', 'creditos', 'proponente']

    def __init__(self, *args, **kwargs):
        super(AsignaturaModelForm, self).__init__(*args, **kwargs)
        self.fields['programa'].required = True

        
class CursoModelForm(forms.ModelForm):

    aula = forms.CharField(max_length=80, help_text='Escriba "Unidad de Posgrado" para solicitar espacio.')
    sede = forms.ChoiceField(required=True, choices=(('CDMX', 'CDMX'),
                                        ('Morelia', 'Morelia'),
                                        (u'León', u'León')))
    
    class Meta:
        model = Curso
        labels = {
            "academicos": "Académicos"
        }
        exclude = ['convocatoria', 'grupo', 'year', 'semestre',
                   'entidad', 'profesores', 'contacto', 
                   'intersemestral', 'activo', 'asignatura', 'status', ]
        widgets = {
            'academicos': autocomplete.ModelSelect2Multiple(url='academico-autocomplete')
        }

    def __init__(self, *args, **kwargs):

        super(CursoModelForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('solicitar', 'solicitar'))
        

class CursoConstancia(forms.Form):

    tema = forms.CharField(max_length=300, required=True)
    horas_impartidas = forms.IntegerField(required=True)
    profesor_invitado = forms.CharField()
    


class CursoConstanciaEstudiante(forms.Form):

    estudiante_invitado = forms.CharField(max_length=300, required=True)
    calificacion = forms.DecimalField(max_digits=4,
                                      decimal_places=2,
                                      max_value=10,
                                      min_value=0)
    
    
        
class PerfilModelForm(forms.ModelForm):

    nombre = forms.CharField()
    apellidos = forms.CharField()

    fecha_nacimiento = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1940, 2000)))

    def __init__(self, *args, **kwargs):

        super(PerfilModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(Div(
                HTML("<h2>Datos Personales</h2>"),
                    style="margin-top: 1em;"),
                Div(Column('nombre',
                           'apellidos',
                           'fecha_nacimiento',
                           'genero',
                           'nacionalidad',
                           'curp',
                           'rfc',
                           'headshot'),
                    Class="panel-body"),

                Div(HTML(u"<h2>Información de contacto</h2>"),
                    style="margin-top: 1em;"),
                Div(Column('telefono',
                           'telefono_movil',
                           'website',
                           'direccion1',
                           'codigo_postal'),
                    Class="panel-body"),
                Class="panel panel-default"),
            Submit('guardar', 'guardar'))

    class Meta:
        model = Perfil
        exclude = ['user', ]


class EstudianteAutoregistroForm(forms.Form):

    proyecto = forms.CharField()
    campo_conocimiento = forms.ModelChoiceField(
        queryset=CampoConocimiento.objects.all())

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('proyecto', size=70),
        'campo_conocimiento',
        FormActions(
            Submit('registrarme', 'Registrarme', css_class="btn-primary"))
    )


class EstudianteModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(EstudianteModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('guardar', 'guardar'))

    class Meta:
        model = Estudiante
        exclude = ['user', ]



class AcademicoPerfilModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AcademicoPerfilModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(Div(HTML("<h1 class='panel-title'>"
                         + u"Generales</h1>"),
                    Class="panel-heading"),
                Div(
                    Column(
                        'anexo_CV',
                        HTML('<hr />'),
                        'anexo_solicitud',
                        HTML(u"""
Instrucciones: anexar carta solicitud en papel membreteado y firmada.
<ul>
<li>
<a href='https://github.com/sostenibilidad-unam/posgrado/files/2278991/Formato.carta.de.solicitud.acreditacion-reacreditacion.de.tutores.nvo.sistema.docx'>
Descargar formato de carta de solicitud acreditación/reacreditación de tutores.</a></li>
<li>
<a href='https://github.com/sostenibilidad-unam/posgrado/files/2278987/Linemientos.para.proyectos.Posgrado.Ciencias.de.la.Sostenibilidad.pdf'>
Consultar los lineamientos para el desarrollo y evaluación de proyectos.</a></li>
</ul>
<hr />
                        """),
                        'ultimo_grado',
                        HTML('<hr />'),
                        'estimulo_UNAM',
                        'nivel_SNI',
                        'CVU',),
                    Class="panel-body")),
            Div(HTML(u"""<h1 class='panel-title'>
                      Disponibilidad
                     </h1>
                         ¿Estaría usted interesado en formar parte de
                         la plantilla pública de tutores del Posgrado
                         para que los aspirantes y alumnos puedan
                         contactarlo y solicitar su asesoría? En ese
                         caso favor de especificar su disponibilidad:
                         """)),
             Div(Column('disponible_tutor', "disponible_miembro"),
                 Class="panel panel-default"),
             Submit('guardar', 'guardar'),
        )

    class Meta:
        model = Academico
        exclude = ['user',
                   'fecha_acreditacion',
                   'acreditacion',
                   'semaforo_maestria',
                   'titulo_honorifico',
                   'semaforo_doctorado',
                   'solicitud', 'comite_academico', 'observaciones']




class PerfilProfesorModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PerfilProfesorModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(Div(HTML("<h1 class='panel-title'>"
                         + u"Generales</h1>"),
                    Class="panel-heading"),
                Div(
                    Column(
                        'anexo_CV',
                        'ultimo_grado'),
                    Class="panel-body")),
            Submit('guardar', 'guardar'),
        )

    class Meta:
        model = Academico
        exclude = ['user',
                   'fecha_acreditacion',
                   'acreditacion',
                   'CVU',
                   'estimulo_UNAM',
                   'nivel_SNI',
                   'semaforo_maestria',
                   'titulo_honorifico',
                   'semaforo_doctorado',
                   'solicitud', 'comite_academico', 'observaciones']
        

class AcademicoResumenCV_reacreditacion_ModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AcademicoResumenCV_reacreditacion_ModelForm,
              self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(HTML(
                     u"En los campos siguientes, si no tiene cantidades "
                     + u"que reportar, por favor llene con ceros."),
                Class="panel-heading"),
            Div(HTML(u"<h2>Formación de estudiantes</h2>"),
                'tesis_doctorado',
                'tesis_doctorado_5',
                'tesis_maestria',
                'tesis_maestria_5',
                'tesis_licenciatura',
                'tesis_licenciatura_5',
                'tutor_principal_otros_programas',
                'comite_doctorado_otros',
                'comite_maestria_otros',
                HTML(u"<h2>Formación de estudiantes en el PCS</h2>"),
                'participacion_tutor_doctorado',
                'participacion_comite_doctorado',
                'participacion_tutor_maestria',
                'participacion_comite_maestria',
                HTML("<h2>Otras actividades</h2>"),
                'otras_actividades',
                HTML("<hr /><h2>Publicaciones</h2>"),
                'articulos_internacionales',
                'articulos_internacionales_5',
                'articulos_nacionales',
                'articulos_nacionales_5',
                'libros',
                'libros_5',
                'capitulos',
                'capitulos_5',
                'top_5',
                HTML("<h3>Otras publicaciones</h3>"),
                'otras_publicaciones',
                Class="panel-body"),
            Submit('guardar', 'guardar'),
        )

    class Meta:
        model = Academico
        exclude = ['user', 'nivel_SNI', 'estimulo_UNAM',
                   'fecha_acreditacion',
                   'acreditacion',
                   'semaforo_maestria',
                   'semaforo_doctorado',
                   'titulo_honorifico',
                   'solicitud', 'comite_academico', 'observaciones']


class AcademicoResumenCVModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AcademicoResumenCVModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(HTML(
                     u"En los campos siguientes, si no tiene cantidades "
                     + u"que reportar, por favor llene con ceros."),
                Class="panel-heading"),
            Div(HTML(u"<h3>Formación de estudiantes</h3>"),
                'tesis_doctorado',
                'tesis_doctorado_5',
                'tesis_maestria',
                'tesis_maestria_5',
                'tesis_licenciatura',
                'tesis_licenciatura_5',
                'tutor_principal_otros_programas',
                'comite_doctorado_otros',
                'comite_maestria_otros',
                HTML("<h4>Otras actividades</h4>"),
                'otras_actividades',
                HTML("<hr /><h3>Publicaciones</h3>"),
                'articulos_internacionales',
                'articulos_internacionales_5',
                'articulos_nacionales',
                'articulos_nacionales_5',
                'libros',
                'libros_5',
                'capitulos',
                'capitulos_5',
                'top_5',
                HTML("<h4>Otras publicaciones</h4>"),
                'otras_publicaciones',
                Class="panel-body"),
            Submit('guardar', 'guardar'),
        )

    class Meta:
        model = Academico
        exclude = ['user', 'nivel_SNI', 'estimulo_UNAM',
                   'fecha_acreditacion',
                   'acreditacion',
                   'semaforo_maestria',
                   'semaforo_doctorado',
                   'titulo_honorifico',
                   'solicitud', 'comite_academico', 'observaciones']


class AcademicoActividadModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AcademicoActividadModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(HTML("<h1 class='panel-title'>"
                     + u"Actividad profesional y de Investigación</h1>"),
                Class="panel-heading"),
            Div(Column(
                "lineas",
                'palabras_clave',
                'motivacion',
                'proyectos_sostenibilidad',
                'proyectos_vigentes',
                HTML(u"""
                Marque los campos de conocimiento y líneas de
                investigación relacionados con los temas de
                su interés y/o experiencia para facilitar la
                búsqueda por parte de los aspirantes y
                alumnos (para elegir más de uno use
                Ctrl+Click en Windows, Cmd+Click en
                Mac). Para más información acerca de los
                Campos de Conocimiento y las Líneas de
                Investigación consulte <a
                href='https://github.com/sostenibilidad-unam/posgrado/files/2233071/Campos.y.lineas.Posgrado.Ciencias.de.la.Sostenibilidad.pdf'>este
                documento</a>."""),
                "lineas_de_investigacion",
                'campos_de_conocimiento',
            ),
                Class="panel-body"),
            Submit('guardar', 'guardar'))

    class Meta:
        model = Academico
        exclude = ['user', 'nivel_SNI', 'estimulo_UNAM',
                   'fecha_acreditacion',
                   'acreditacion',
                   'semaforo_maestria',
                   'semaforo_doctorado',
                   'titulo_honorifico',
                   'solicitud', 'comite_academico', 'observaciones']


class SolicitudCommentForm(forms.Form):

    comentario = forms.CharField(
        widget=forms.Textarea(),
        required=True
    )

    helper = FormHelper()
    helper.layout = Layout(
        Field('comentario', rows="3", cols="40", css_class='input-xlarge'),
        FormActions(
            Submit('comentar', 'comentar', css_class="btn-primary"),
        )
    )


class SolicitudAgendarForm(forms.Form):

    sesion = forms.ModelChoiceField(queryset=Sesion.objects.filter(
        fecha__gt=datetime.now()),
                                    label=u"Sesión")

    helper = FormHelper()
    helper.layout = Layout(
        Field('sesion'),
        FormActions(
            Submit('agendar', 'agendar', css_class="btn-primary"),
        )
    )


class SolicitudDictamenForm(forms.Form):

    comentario = forms.CharField(
        widget=forms.Textarea(),
        required=True
    )

    helper = FormHelper()
    denegar = Submit('denegar', 'denegar', css_class="btn-danger")
    denegar.field_classes.replace('btn-primary', 'btn-danger')

    helper.layout = Layout(
        Field('comentario', rows="3", cols="40", css_class='input-xlarge'),
        FormActions(
            Submit('conceder', 'conceder', css_class="btn-success"),
            denegar
        )
    )


class SolicitudAnexoForm(forms.Form):

    anexo = forms.FileField(required=True)

    # Uni-form
    helper = FormHelper()
#    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        'anexo',
        FormActions(
            Submit('anexar', 'anexar', css_class="btn-primary"),
        )
    )


class GradoAcademicoModelForm(forms.ModelForm):

    fecha_obtencion = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1960, datetime.now().year + 1)))

    class Meta:
        model = GradoAcademico
        exclude = ['user', ]

    def __init__(self, *args, **kwargs):

        super(GradoAcademicoModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            'nivel',
            'grado_obtenido',
            'institucion',
            HTML('<a href="%sinstitucion/agregar/ga/">agregar institucion</a><br /><br />' % settings.APP_PREFIX),
            'facultad',
            'fecha_obtencion',
            Submit('agregar', 'agregar'))


class AdscripcionModelForm(forms.ModelForm):

    class Meta:
        model = Adscripcion
        exclude = ['perfil', ]

    def __init__(self, *args, **kwargs):

        super(AdscripcionModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            'institucion',
            HTML(u'<a href="%sinstitucion/agregar/ad/">agregar institución a la lista</a><br /><br />'
                 % settings.APP_PREFIX),
            'catedra_conacyt',
            'nombramiento',
            'anno_nombramiento',
            Submit('agregar', 'agregar'))


class AsociacionModelForm(forms.ModelForm):

    class Meta:
        model = Adscripcion
        exclude = ['perfil', 'nombramiento', 'anno_nombramiento']

    def __init__(self, *args, **kwargs):
        super(AsociacionModelForm, self).__init__(*args, **kwargs)
        self.fields['institucion'].queryset = Institucion.objects.filter(
            entidad_PCS=True)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            HTML(u'<p>Usted no está adscrito en alguna de las entidades participantes del Posgrado. Elija a la que prefiera asociarse para la comunicación con los representantes en el Comité Académico del Programa.</p>'),
            'institucion',
            Submit('agregar', 'agregar'))


class InstitucionModelForm(forms.ModelForm):

    class Meta:
        model = Institucion
        exclude = ['entidad_PCS']

    def __init__(self, *args, **kwargs):

        super(InstitucionModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('agregar', 'agregar'))




class ProyectoModelForm(forms.ModelForm):

    class Meta:
        model = Proyecto
        exclude = ['estudiante', 'solicitud', 'aprobado']

    def __init__(self, *args, **kwargs):

        super(ProyectoModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('guardar', 'guardar'))


# class CursoModelForm(forms.ModelForm):

#     class Meta:
#         model = Curso



class EstudianteCargarForm(forms.Form):

    ingreso = forms.IntegerField(initial=datetime.now().year,
                                 min_value=datetime.now().year)
    semestre = forms.ChoiceField(choices=[(1, 1),
                                          (2, 2)])
    lista = forms.FileField(required=True)

    helper = FormHelper()
    helper.layout = Layout(
        Field('ingreso'),
        Field('semestre'),
        Field('lista'),
        FormActions(
            Submit('cargar', 'cargar', css_class="btn-primary"),
        )
    )
