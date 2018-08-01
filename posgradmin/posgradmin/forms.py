# coding: utf-8
from datetime import datetime
from django import forms
from django.forms import extras
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import PrependedText, AppendedText, FormActions
from django.utils.safestring import mark_safe
from posgradmin.models import Perfil, Estudiante, Academico, \
    CampoConocimiento, GradoAcademico, Institucion, Comite, \
    Proyecto, Catedra, Sesion, Adscripcion
from django.conf import settings


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


class PerfilModelForm(forms.ModelForm):

    nombre = forms.CharField()
    apellidos = forms.CharField()

    fecha_nacimiento = forms.DateField(
        widget=extras.SelectDateWidget(years=range(1940, 2000)))

    def __init__(self, *args, **kwargs):

        super(PerfilModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(Div(HTML("<h1 class='panel-title'>Datos Personales</h1>"),
                    Class="panel-heading"),
                Div(Column('nombre',
                           'apellidos',
                           'fecha_nacimiento',
                           'genero',
                           'nacionalidad',
                           'curp',
                           'rfc',
                           'headshot'),
                    Class="panel-body"),

                Div(HTML(u"<h1 class='panel-title'>Información de contacto</h1>"),
                    Class="panel-heading"),
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


class AcademicoModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AcademicoModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(Div(HTML("<h1 class='panel-title'>"
                         + u"Participación en el Programa</h1>"),
                    Class="panel-heading"),
                Div(Column('titulo',
                           'nivel_PRIDE',
                           'nivel_SNI',
                           'CVU',),
                    Class="panel-body"),
                Div(HTML(u"<h1 class='panel-title'>Resumen Curricular</h1>"
                         + "En los campos siguientes, si no tiene cantidades "
                         + u"que reportar, por favor llene con ceros."),
                    Class="panel-heading"),
                Div(Column('tesis_licenciatura',
                           'tesis_licenciatura_5',
                           'tesis_maestria',
                           'tesis_maestria_5',
                           'tesis_doctorado',
                           'tesis_doctorado_5',
                           'participacion_comite_maestria',
                           'participacion_comite_doctorado',
                           'participacion_tutor_maestria',
                           'participacion_tutor_doctorado',
                           'tutor_otros_programas',
                           'tutor_principal_otros_programas',
                           'articulos_internacionales',
                           'articulos_internacionales_5',
                           'articulos_nacionales',
                           'articulos_nacionales_5',
                           'libros',
                           'libros_5',
                           'capitulos',
                           'capitulos_5'),
                    Class="panel-body"),
                Div(HTML("<h1 class='panel-title'>"
                         + u"Actividad profesional y de Investigación</h1>"),
                    Class="panel-heading"),
                Div(Column(
                    HTML(u"Para más información acerca de los Campos de Conocimiento y las Líneas de Investigación consulte <a href='https://github.com/sostenibilidad-unam/posgrado/files/2233071/Campos.y.lineas.Posgrado.Ciencias.de.la.Sostenibilidad.pdf'>este documento</a>."),
                    "lineas_de_investigacion",
                    'campos_de_conocimiento',
                    HTML("<hr>"),
                    "lineas",
                    'palabras_clave',
                    'motivacion',
                    'proyectos_sostenibilidad',
                    'proyectos_vigentes'),
                    Class="panel-body"),
                Div(HTML("<h1 class='panel-title'>"
                         + u"Disponibilidad</h1>"),
                    Class="panel-heading"),
                Div(Column('disponible_tutor', "disponible_miembro"),
                    Class="panel-body"),
                Submit('guardar', 'guardar'),
                Class="panel panel-default"),
        )

    class Meta:
        model = Academico
        exclude = ['user', 'tutor',
                   'fecha_acreditacion', 'acreditacion',
                   'DGEE', 'solicitud', 'comite_academico', 'observaciones']


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
        widget=extras.SelectDateWidget(years=range(1960, datetime.now().year + 1)))

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
            HTML('<a href="%sinstitucion/agregar">agregar institucion</a><br /><br />' % settings.APP_PREFIX),
            'facultad',
            'fecha_obtencion',
            'promedio',
            'documento',
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
            HTML(u'<a href="%sinstitucion/agregar">agregar institución a la lista</a><br /><br />'
                 % settings.APP_PREFIX),
            HTML(u'<p>Si no está usted adscrito en alguna de las entidades participantes del Posgrado, elija una marcada como "entidad del PCS" con la que crea que prefiera estar asociado para la comunicación con los representantes en el Comité Académico del Programa, y marque la siguiente casilla.</p>'),
            'asociacion_PCS',
            Submit('agregar', 'agregar'))

    def clean_asociacion_PCS(self):
        ins = self.cleaned_data['institucion']
        asoc = self.cleaned_data['asociacion_PCS']
        if asoc and not ins.entidad_PCS:
            raise forms.ValidationError(
                u"Ha elegido asociarse al PCS a través de una institución que no es entidad.")

        return asoc


class InstitucionModelForm(forms.ModelForm):

    class Meta:
        model = Institucion
        exclude = ['entidad_PCS']

    def __init__(self, *args, **kwargs):

        super(InstitucionModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('agregar', 'agregar'))


class ComiteTutoralModelForm(forms.ModelForm):
    tutor = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    cotutor = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    miembro1 = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    miembro2 = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True),
        required=False)

    miembro3 = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True),
        required=False)

    class Meta:
        model = Comite
        exclude = ['solicitud', 'tipo', 'estudiante',
                   'miembro1', 'miembro2', 'miembro3',
                   'miembro4', 'miembro5']

    def __init__(self, *args, **kwargs):

        super(ComiteTutoralModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('elegir', 'elegir'))


class CandidaturaModelForm(forms.ModelForm):
    presidente = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    secretario = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    miembro1 = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    miembro2 = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True),
        required=False)

    miembro3 = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True),
        required=False)

    class Meta:
        model = Comite
        exclude = ['solicitud', 'tipo', 'estudiante',
                   'miembro1', 'miembro2', 'miembro3',
                   'miembro4', 'miembro5']

    def __init__(self, *args, **kwargs):

        super(CandidaturaModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('elegir', 'elegir'))


class JuradoGradoModelForm(forms.ModelForm):
    presidente = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    secretario = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    vocal = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    suplente = forms.ModelChoiceField(
        queryset=Academico.objects.filter(tutor=True))

    class Meta:
        model = Comite
        exclude = ['solicitud', 'tipo', 'estudiante',
                   'miembro1', 'miembro2', 'miembro3',
                   'miembro4', 'miembro5']

    def __init__(self, *args, **kwargs):

        super(JuradoGradoModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('elegir', 'elegir'))


class ProyectoModelForm(forms.ModelForm):

    class Meta:
        model = Proyecto
        exclude = ['estudiante', 'solicitud', 'aprobado']

    def __init__(self, *args, **kwargs):

        super(ProyectoModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('guardar', 'guardar'))


class CatedraModelForm(forms.ModelForm):

    class Meta:
        model = Catedra
        exclude = ['solicitud', 'profesor']

    def __init__(self, *args, **kwargs):

        super(CatedraModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.layout.append(Submit('registrar', 'registrar'))


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
