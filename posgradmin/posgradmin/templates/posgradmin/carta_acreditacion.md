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

{{ dr }}{{ ac.academico}}
\
Presente
\
\
\

Por este medio le informo que el Comité Académico del Programa de
Posgrado en Ciencias de la Sostenibilidad aprobó su acreditación como
{% if ac.academico.user.perfil.genero == 'M' %}tutor{% else %}tutora{% endif %} de {% if ac.acreditacion == 'M' %}Maestría{% else %}Doctorado{% endif %} en este Programa de Posgrado.

Es una buena noticia para el Programa saber que a partir de ahora
contaremos con su participación. Sin duda su experiencia y compromiso
contribuirán a la formación de nuestros estudiantes, a través de su
aportación en comités conformados por tutores de diversas disciplinas.
\
\

Me despido enviándole un cordial saludo.

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
