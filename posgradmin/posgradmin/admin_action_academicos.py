# coding: utf-8

from .models import Perfil, Academico, \
    GradoAcademico, Institucion, CampoConocimiento, \
    Adscripcion, LineaInvestigacion
from django.http import HttpResponse
import csv

from openpyxl import Workbook



def exporta_resumen_academicos(modeladmin, request, queryset):

    response = HttpResponse(content_type='application/vnd.ms-excel', charset='utf-8')
    response['Content-Disposition'] = 'attachment; filename="academicos_resumen.xlsx"'

    wb = Workbook()
    ws = wb.active

    row = u"nombre|grado|acreditacion|adscripcion|asociacion|tesis_licenciatura|tesis_licenciatura_5|tesis_maestria|tesis_maestria_5|tesis_doctorado|tesis_doctorado_5|comite_doctorado_otros|comite_maestria_otros|participacion_comite_maestria|participacion_tutor_maestria|participacion_comite_doctorado|participacion_tutor_doctorado|articulos_internacionales_5|articulos_nacionales_5|articulos_internacionales|articulos_nacionales|capitulos|capitulos_5|libros|libros_5|palabras_clave|lineas|campos|faltantes".split("|")

    ws.append(row)


    for a in queryset:
        if a.perfil_personal_completo:

            if a.user.perfil.adscripcion_set.filter(asociacion_PCS=True).count() > 0:
                asociacion = a.user.perfil.adscripcion_set.filter(asociacion_PCS=True).first()
                adscripcion = a.user.perfil.adscripcion_set.filter(asociacion_PCS=False).first()

            elif a.user.perfil.adscripcion_set.filter(institucion__entidad_PCS=True,
                                                    asociacion_PCS=False).count() > 0:
                adscripcion = a.user.perfil.adscripcion_set.filter(institucion__entidad_PCS=True,
                                                                   asociacion_PCS=False).first()
                asociacion = ""



        else:
            adscripcion = ""
            asociacion = ""

        grado = a.user.gradoacademico_set.last()
        if grado is not None:
            grado = grado.grado_obtenido
        else:
            grado = ""

        row = [
            a.user.get_full_name(),
            grado,
            a.acreditacion,
            str(adscripcion),
            str(asociacion).replace('None', ''),
            a.tesis_licenciatura,
            a.tesis_licenciatura_5,
            a.tesis_maestria,
            a.tesis_maestria_5,
            a.tesis_doctorado,
            a.tesis_doctorado_5,
            a.comite_doctorado_otros,
            a.comite_maestria_otros,
            a.participacion_comite_maestria,
            a.participacion_tutor_maestria,
            a.participacion_comite_doctorado,
            a.participacion_tutor_doctorado,
            a.articulos_internacionales_5,
            a.articulos_nacionales_5,
            a.articulos_internacionales,
            a.articulos_nacionales,
            a.capitulos,
            a.capitulos_5,
            a.libros,
            a.libros_5,
            a.palabras_clave.replace(u'\r\n', u';'),
            u";".join([l.nombre for l in a.lineas_de_investigacion.all()]),
            u";".join([c.nombre for c in a.campos_de_conocimiento.all()]),
            a.carencias_actividad().replace(u"\n", u";"),
        ]
        ws.append(row)

    wb.save(response)

    return response





def exporta_emails_cursos(modeladmin, request, queryset):

    response = HttpResponse(content_type='application/vnd.ms-excel', charset='utf-8')
    response['Content-Disposition'] = 'attachment; filename="correos_cursos.xlsx"'

    wb = Workbook()
    ws = wb.active

    ws.append(["Nombre del curso",
               "Año",
               "Semestre",
               "Nombre del profesor",
               "Correo del profesor"])

    for c in queryset:
        for a in c.academicos.all():
            row = [
                c.asignatura.asignatura,
                c.year,
                c.semestre,
                a.user.get_full_name(),
                a.user.email
            ]
            ws.append(row)

    wb.save(response)

    return response
