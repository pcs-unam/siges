# coding: utf-8
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, FormActions


class MessageForm(forms.Form):
    text_input = forms.CharField()

    textarea = forms.CharField(
        widget=forms.Textarea(),
    )

    radio_buttons = forms.ChoiceField(
        choices=(
            ('option_one',
             "Option one is this and that be sure to include why it's great"),
            ('option_two',
             "Something else and selecting it will deselect option one")
        ),
        widget=forms.RadioSelect,
        initial='option_two',
    )

    checkboxes = forms.MultipleChoiceField(
        choices=(
            ('option_one',
             "Option one is this and that be sure to include why it's great"),
            ('option_two',
             'Option two can also be checked and included in form results'),
            ('option_three',
             'Option three')
        ),
        initial='option_one',
        widget=forms.CheckboxSelectMultiple,
        help_text="<strong>Note:</strong> Labels surround all the options" +
        "for much larger click areas and a more usable form.",
    )

    appended_text = forms.CharField(

        help_text="Here's more help text"
    )

    prepended_text = forms.CharField()

    prepended_text_two = forms.CharField()

    multicolon_select = forms.MultipleChoiceField(
        choices=(('1', '1'),
                 ('2', '2'),
                 ('3', '3'),
                 ('4', '4'),
                 ('5', '5')),
    )

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('text_input', css_class='input-xlarge'),
        Field('textarea', rows="3", css_class='input-xlarge'),
        'radio_buttons',
        Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
        AppendedText('appended_text', '.00'),
        'multicolon_select',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )


class AsuntoEstudiantilForm(forms.Form):

    tipo = forms.ChoiceField(
        choices=(
            ('seleccionar_jurado',
             "Selección de jurado de grado o de candidatura"),
            ('registrar_actividad_complementaria',
             "Registro de actividad complementaria"),
            ('solicitar_candidatura',
             "Solicitud de examen de candidtaura"),
            ("cambiar_comite_tutoral",
             "Cambiar comité tutoral"),
            ("cambiar_titulo_proyecto",
             "Solicitud de cambio de título de proyecto"),
            ("cambiar_campo_conocimiento",
             "Cambio de campo de conocimiento"),
            ("reportar_suspension",
             "Reportar suspensión")
        ),
        widget=forms.RadioSelect,
        initial='option_two',
    )

    resumen = forms.CharField()

    descripcion = forms.CharField(
        widget=forms.Textarea(),
    )

    anexo = forms.FileField()

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        'tipo',
        Field('resumen', css_class='input-xlarge'),
        Field('descripcion', rows="3", css_class='input-xlarge'),
        Field('anexo'),

        FormActions(
            Submit('someter', 'Someter Solicitud', css_class="btn-primary"),
            Submit('cancel', 'Cancela'),
        )
    )
