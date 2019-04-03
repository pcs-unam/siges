---
title: {{ a }}
layout: page
permalink: tutores/{{ a.user.username }}/
---

Acreditación: **{{ a.show_acreditacion }}**

{% if a.disponible_tutor %}
 - Disponible como tutor principal (dirección de alumnos).
{% endif %}
{% if a.disponible_miembro %}
 - Disponible como miembro de comité tutor (asesoría de alumnos)
{% endif %}


# Información de contacto

 - <{{ a.user.email }}>

{% if a.user.perfil.website %}
 - <{{ a.user.perfil.website }}>
{% endif %}

# Adscripción

{% for ad in a.user.perfil.adscripcion_set.all %}
 - {{ ad }} {% if ad.catedra_conacyt %}Cátedra CONACYT{% endif %} {% if not ad.asociacion_PCS %} {{ ad.nombramiento }} desde {{ ad.anno_nombramiento }}
 {% endif %}
{% endfor %}


# Grados académicos

{% for grado in a.user.gradoacademico_set.all %}
 - **{{ grado.grado_obtenido }}**, {{ grado.institucion }}, nivel {{ grado.nivel }} obtenido el {{ grado.fecha_obtencion }}
{% endfor %}

## Perfil académico

# Temas de Interés

{{ a.lineas }}

# Palabras clave

{% for p in palabras_clave %}
 - {{ p }}
{% endfor %}

# Cinco publicaciones más destacadas en temas relacionados con las Ciencias de la Sostenibilidad

{{ a.top_5 }}

# Principales proyectos relacionados con Ciencias de la Sostenibilidad durante los últimos cinco años

{{ a.proyectos_sostenibilidad }}

# Proyectos vigentes en los que pueden participar alumnos del PCS.

{{ a.proyectos_vigentes }}

# Líneas de Investigación

{% for l in a.lineas_de_investigacion.all %}
 - {{ l }}
{% endfor %}

# Campos de Conocimiento
{% for c in a.campos_de_conocimiento.all %}
 - {{ c }}
{% endfor %}


![wordcloud](https://sostenibilidad.posgrado.unam.mx/media/perfil-academico/{{ a.id }}/wordcloud.png)
