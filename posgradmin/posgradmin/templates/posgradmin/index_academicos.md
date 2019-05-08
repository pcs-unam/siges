{% load md2 %}
---
title: Tutores
layout: page
permalink: /tutores/
pleca: /assets/plecas/p{{ pleca|stringformat:"02d" }}.jpg
menu: true
---

## Maestría

<table>
<thead>
<tr><th>Tutor</th><th>Adscripción</th><th>Campos de Conocimiento</th><th>Palabras clave</th><th>Dirección de alumnos</th><th>Asesoría de alumnos</th></tr>
</thead>
<tbody>
{% for a in maestria %}<tr>
<td>[{{ a|title }}]({{ a.user.username }}/)</td>
<td><ul>{% for ad in a.user.perfil.adscripcion %}<li>{{ ad }}</li>{% endfor %}</ul></td>
<td><ul>{% for c in a.campos_de_conocimiento.all %}<li>{{ c }}</li>{% endfor %}</ul></td>
<td>{{ a.palabras_clave|markdown }}</td>
<td>{% if a.disponible_tutor %}&#10004;{% endif %}</td>
<td>{% if a.disponible_miembro %}&#10004;{% endif %}</td></tr>{% endfor %}
</tbody>
</table>


## Doctorado

<table>
<thead>
<tr><th>Tutor</th><th>Adscripción</th><th>Líneas de Investigación</th><th>Palabras clave</th><th>Dirección de alumnos</th><th>Asesoría de alumnos</th></tr>
</thead>
<tbody>
{% for a in doctorado %}<tr>
<td>[{{ a|title }}]({{ a.user.username }}/)</td>
<td><ul>{% for ad in a.user.perfil.adscripcion %}<li>{{ ad }}</li>{% endfor %}</ul></td>
<td><ul>{% for c in a.lineas_de_investigacion.all %}<li>{{ c }}</li>{% endfor %}</ul></td>
<td>{{ a.palabras_clave|markdown }}</td>
<td>{% if a.disponible_tutor %}&#10004;{% endif %}</td>
<td>{% if a.disponible_miembro %}&#10004;{% endif %}</td></tr>{% endfor %}
</tbody>
</table>

