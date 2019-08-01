---
title: {{ linea }}
layout: page
permalink: /tutores/{{ link }}/
pleca: /assets/plecas/p{{ pleca|stringformat:"02d" }}.jpg
---


| Tutor | Adscripción |Disponible como tutor principal (dirección de alumnos) | Disponible como miembro de comité tutor (asesoría de alumnos) |
|-------|-------------|-------------------------------------------|---------------------------------------------------------------|
{% for a in academicos %}| [{{ a|title }}](/tutores/{{ a.user.username }}/) | {{ a.user.perfil.adscripcion.first }} | {% if a.disponible_tutor %}&#10004;{% endif %} | {% if a.disponible_miembro %}&#10004;{% endif %} |
{% endfor %} 
