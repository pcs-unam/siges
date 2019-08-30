from .models import Perfil, Academico, \
    GradoAcademico, Institucion, CampoConocimiento, \
    Adscripcion, LineaInvestigacion
from django.http import HttpResponse
import csv
import tempfile


def exporta_resumen_academicos(modeladmin, request, queryset):
    rows = "titulo|nombre|grado|acreditacion|tesis_licenciatura|tesis_licenciatura_5|tesis_maestria|tesis_maestria_5|tesis_doctorado|tesis_doctorado_5|comite_doctorado_otros|comite_maestria_otros|participacion_comite_maestria|participacion_tutor_maestria|participacion_comite_doctorado|participacion_tutor_doctorado|articulos_internacionales_5|articulos_nacionales_5|articulos_internacionales|articulos_nacionales|capitulos|capitulos_5|libros|libros_5|palabras_clave|lineas|campos|adscripcion|asociacion|faltantes\n".replace("|", ",")
    for a in queryset:
        if a.perfil_personal_completo:
            titulo = a.user.perfil.titulo
                
            if a.user.perfil.adscripcion_set.filter(asociacion_PCS=True).count > 0:
                asociacion = a.user.perfil.adscripcion_set.filter(asociacion_PCS=True).first()
                adscripcion = a.user.perfil.adscripcion_set.filter(asociacion_PCS=False).first()
                
            elif a.user.perfil.adscripcion_set.filter(institucion__entidad_PCS=True,
                                                    asociacion_PCS=False).count > 0:
                adscripcion = a.user.perfil.adscripcion_set.filter(institucion__entidad_PCS=True,
                                                                   asociacion_PCS=False).first()
                asociacion = ""

                
                
        else:
            titulo = ""
            adscripcion = ""
            asociacion = ""

        grado = a.user.gradoacademico_set.last()
        if grado is not None:
            grado = grado.grado_obtenido
        else:
            grado = ""
            
        row = [
            titulo,
            a.user.get_full_name(),
            grado,
            a.acreditacion,
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
            ";".join([str(l).decode('utf-8') for l in a.lineas_de_investigacion.all()]),
            ";".join([str(c).decode('utf-8') for c in a.campos_de_conocimiento.all()]),
            adscripcion,
            asociacion,
            unicode(a.carencias()).replace(u"\n", u";"),
        ]
        strrow = u",".join([unicode(cell).replace(',', ';') for cell in row]) + u"\n"
        strrow = strrow.replace('None', '')
        rows += strrow

        
    response = HttpResponse(
        rows,
        content_type="application/csv; charset=utf-8")
    
    response['Content-Disposition'] \
        = 'attachment; filename="academicos_resumen.csv"'
    
    return response


