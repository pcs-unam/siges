# coding: utf-8
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import PrependedText, AppendedText, FormActions
from django.utils.safestring import mark_safe
from posgradmin.models import Perfil, Estudiante, Academico, CampoConocimiento


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

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('tipo',
              onfocus=mark_safe("$('#id_resumen').val(this.value);")),

        Field('resumen', size=70),

        # Field('resumen', css_class='input-xlarge'),
        Field('descripcion', rows="3", cols="70", css_class='input-xlarge'),
        Field('anexo'),

        FormActions(
            Submit('someter', 'Someter Solicitud', css_class="btn-primary"),
            Submit('cancel', 'Cancelar'),
        )
    )


class PerfilModelForm(forms.ModelForm):

    nombre = forms.CharField()
    apellidos = forms.CharField()

    def __init__(self, *args, **kwargs):

        super(PerfilModelForm, self).__init__(*args, **kwargs)

        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper(self)
#        self.helper.form_class = 'form-horizontal'
        # You can dynamically adjust your layout
        # self.helper.form_class = 'form-inline'
        # self.helper.field_template = 'bootstrap3/layout/inline_field.html'

        self.helper.layout = Layout(
            Div(Div(HTML("<h1 class='panel-title'>Datos Personales</h1>"),
                    Class="panel-heading"),
                Div(Column('nombre',
                           'apellidos',
                           'fecha_nacimiento',
                           'genero',
                           'nacionalidad',
                           'curp',
                           'rfc'),
                    Class="panel-body"),

                Div(HTML(u"<h1 class='panel-title'>Información de contacto</h1>"),
                    Class="panel-heading"),
                Div(Column('telefono',
                           'telefono_movil',
                           'email2',
                           'website',
                           'direccion1',
                           'direccion2',
                           'codigo_postal'),
                    Class="panel-body"),
                Class="panel panel-default"),
            Submit('save', 'save'))

    class Meta:
        model = Perfil
        exclude = ['user', ]


class EstudianteAutoregistroForm(forms.Form):

    proyecto = forms.CharField()
    campo_conocimiento = forms.ModelChoiceField(
        queryset=CampoConocimiento.objects.all())

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('proyecto', size=70),
        'campo_conocimiento',
        FormActions(
            Submit('registrarme', 'Registrarme', css_class="btn-primary"),
            Submit('cancel', 'Cancelar'),
        )
    )


class EstudianteModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(EstudianteModelForm, self).__init__(*args, **kwargs)

        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        # You can dynamically adjust your layout
        self.helper.layout.append(Submit('save', 'save'))

    class Meta:
        model = Estudiante
        exclude = ['user', ]


class AcademicoModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(AcademicoModelForm, self).__init__(*args, **kwargs)

        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        # You can dynamically adjust your layout
        self.helper.layout.append(Submit('save', 'save'))

    class Meta:
        model = Academico
        exclude = ['user', 'tutor', 'profesor',
                   'fecha_acreditacion', 'acreditacion', 'entidad']


class SolicitudCommentForm(forms.Form):

    comentario = forms.CharField(
        widget=forms.Textarea(),
        required=True
    )
    # Uni-form
    helper = FormHelper()
#    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('comentario', rows="3", cols="40", css_class='input-xlarge'),
        FormActions(
            Submit('comentar', 'comentar', css_class="btn-primary"),
        )
    )
