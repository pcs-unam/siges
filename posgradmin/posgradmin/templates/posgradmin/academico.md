---
title: {{ a }}
layout: page
pleca: /assets/plecas/p{{ pleca|stringformat:"02d" }}.jpg
permalink: /tutores/{{ a.user.username }}/
---

Acreditación: **{{ a.show_acreditacion }}**

{% if a.disponible_tutor %}
 - Disponible como tutor principal (dirección de alumnos).
{% endif %}
{% if a.disponible_miembro %}
 - Disponible como miembro de comité tutor (asesoría de alumnos)
{% endif %}
{% if not a.disponible_tutor and not a.disponible_miembro %}
 - Sin disponibilidad para estudiantes.
{% endif %}



# Información de contacto

 - <{{ a.user.email }}>

{% if a.user.perfil.website %}
 - {{ a.user.perfil.website|urlize }}
{% endif %}



# Adscripción

{% for ad in a.user.perfil.adscripcion_set.all %}
{% if not ad.asociacion_PCS %}
 - {{ ad }} {% if ad.catedra_conacyt %}Cátedra CONACYT{% endif %}
{% endif %}
{% endfor %}




## Perfil académico


# Grados académicos

{% for grado in a.user.gradoacademico_set.all %}
 - **{{ grado.grado_obtenido }}**, {{ grado.institucion }}, nivel {{ grado.nivel }} obtenido el {{ grado.fecha_obtencion }}
{% endfor %}



# Temas de Interés

{{ a.lineas }}



# Palabras clave

{% for p in palabras_clave %}
 - {{ p }}
{% endfor %}



# Cinco publicaciones más destacadas en temas relacionados con las Ciencias de la Sostenibilidad

{{ a.top_5|linebreaksbr }}




# Principales proyectos relacionados con Ciencias de la Sostenibilidad durante los últimos cinco años

{{ a.proyectos_sostenibilidad|linebreaksbr }}




# Proyectos vigentes en los que pueden participar alumnos del PCS

{{ a.proyectos_vigentes|linebreaksbr }}




{% if a.acreditacion == 'D' %}
# Líneas de Investigación

{% for l in a.lineas_de_investigacion.all %}
 - {{ l }}
{% endfor %}

{% endif %}



# Campos de Conocimiento
{% for c in a.campos_de_conocimiento.all %}
 - {{ c }}
{% endfor %}


![wordcloud](https://sostenibilidad.posgrado.unam.mx/media/perfil-academico/{{ a.id }}/wordcloud.png)
