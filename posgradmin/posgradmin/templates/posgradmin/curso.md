---
title: "{{ curso.asignatura.asignatura }}"
layout: page
pleca: /assets/plecas/p{{ pleca|stringformat:"02d" }}.jpg
permalink: /cursos/{{ curso_slug }}/
---

| Semestre | {{ curso.year }}-{{ curso.semestre }} |
| Entidad | {{ curso.entidad|default:"" }} |
| Clave | {{ curso.asignatura.clave|default:"" }} |
| Grupo | {{ curso.grupo|default:"" }} |
| Créditos | {{ curso.asignatura.creditos }} |
| Tipo | {{ curso.asignatura.tipo }} |{% if curso.asignatura.campos_de_conocimiento.count %}
| Campo de Conocimiento | {{ curso.asignatura.campos_de_conocimiento.all|join:" // " }} |{% endif %}
| Sede | {{ curso.sede|default:"" }} |
| Aula | {{ curso.aula|default:"" }} |
| Día(s) y horario | {{ curso.horario|default:"" }} |
| Profesores | {{ academicos|safeseq|join:', ' }} |
{% if curso.contacto %}| Contacto | {{ curso.contacto|linebreaksbr|default:"" }} |{% endif %}
{% if curso.asignatura.programa_url %}| Descargables |  [Programa]({{ curso.asignatura.programa.url }}) |{% endif %}
