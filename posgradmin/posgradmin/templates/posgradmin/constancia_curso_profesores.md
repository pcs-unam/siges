---
papersize: letter
geometry:
- top=30mm
- left=30mm
---


\pagenumbering{gobble}

\rightline{Ciudad Universitaria, Cd. Mx., a {{ fecha }} }
\ 
\
\
\
\ 
\
\
\ 
A quien corresponda,
\
\
\
\
\
\ 

Por medio de la presente se hace constar que {% if academicos|length == 1 %}{{ academicos|first }} impartió {% elif academicos|length == 2 %}{{ academicos.0 }} y {{ academicos.1 }} impartieron {% elif academicos|length > 2 %} {% for a in academicos %}{% if forloop.first %}{{ a }}{% else %}{% if forloop.last %} y {{ a }}{% else %}, {{ a }}{% endif %}{% endif %}{% endfor %} impartieron{% endif %}{% if curso.asignatura.tipo == "Seminario de Doctorado" %} la actividad "{{ curso.asignatura.get_asignatura }}" durante el semestre {{ curso.year}}-{{ curso.semestre }}. Dicha actividad forma parte del Doctorado en Ciencias de la Sostenibilidad de la Universidad Nacional Autónoma de México.{% else %} el curso "{{ curso.asignatura.asignatura }}" durante el semestre {{ curso.year }}-{{ curso.semestre }}. Dicho curso forma parte de la Maestría en Ciencias de la Sostenibilidad de la Universidad Nacional Autónoma de México y tiene valor de {{ curso.asignatura.creditos }} créditos, lo que equivale a {% widthratio curso.asignatura.creditos 1 8 %} horas.{% endif %}

\
\
Se extiende la presente para los fines que a los interesados convengan.
\
\
\
\
\
Atentamente,
\
![]({{ firma }})
\
Dr. Alonso Aguilar Ibarra\
Coordinador
\
Posgrado en Ciencias de la Sostenibilidad, UNAM
