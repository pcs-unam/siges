---
title: Tutores
layout: page
permalink: /tutores/
pleca: /assets/plecas/p{{ pleca|stringformat:"02d" }}.jpg
menu: true
---

## Maestría

| Tutor | Disponible como tutor principal (dirección de alumnos) | Disponible como miembro de comité tutor (asesoría de alumnos) |
|-------|--------------------------------------------------------|---------------------------------------------------------------|
{% for a in maestria %}| [{{ a|title }}]({{ a.user.username }}/) | {% if a.disponible_tutor %}&#10004;{% endif %} | {% if a.disponible_miembro %}&#10004;{% endif %} |
{% endfor %}


## Doctorado

| Tutor | Disponible como tutor principal (dirección de alumnos) | Disponible como miembro de comité tutor (asesoría de alumnos) |
|-------|--------------------------------------------------------|---------------------------------------------------------------|
{% for a in doctorado %}| [{{ a|title }}]({{ a.user.username }}/) | {% if a.disponible_tutor %}&#10004;{% endif %} | {% if a.disponible_miembro %}&#10004;{% endif %} |
{% endfor %}
