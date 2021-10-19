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
Por medio de la presente se hace constar {{ estudiante_invitado }} cursó la asignatura “{{ curso.asignatura.asignatura }}", obteniendo una calificación final de {{ calificacion }}. El curso forma parte de la Maestría en Ciencias de la Sostenibilidad de la Universidad Nacional Autónoma de México. Dicho curso fue impartido durante el semestre {{ curso.year }}-{{ curso.semestre }}, con un total de {{ curso.asignatura.horas }} horas.
\
\
Se extiende la presente para los fines que a la persona interesada convengan.
\
\
\
\
\
Atentamente,
\
\
\
\
{{ profesor }}
\
Profesor
\
Posgrado en Ciencias de la Sostenibilidad, UNAM
