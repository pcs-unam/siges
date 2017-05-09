# coding: utf-8
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, FormActions
from django.utils.safestring import mark_safe
from posgradmin.models import Perfil, Estudiante, Academico


class AsuntoForm(forms.Form):

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

        super(EstudianteModelForm, self).__init__(*args, **kwargs)

        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        # You can dynamically adjust your layout
        self.helper.layout = Layout('nombre',
                                    'apellidos',

                                    'fecha_nacimiento',
                                    'nacionalidad',
                                    'genero',

                                    'CURP',
                                    'RFC',

                                    'telefono',
                                    'telefono_movil',
                                    'email2',
                                    'website',

                                    'direccion1',
                                    'direccion2',
                                    'codigo_postal',

                                    Submit('save', 'save'))

    class Meta:
        model = Perfil
        exclude = ['user', ]


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
        exclude = ['user', 'tutor', 'profesor', 'fecha_acreditacion', 'acreditacion', 'entidad']

