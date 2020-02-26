"""
pipe me into ./manage.py shell
"""

import posgradmin.models as models

for a in models.Academico.objects.all():
    print(a)
    if a.acreditacion == 'D' or a.acreditacion == 'M' or a.acreditacion == 'E':
        if a.fecha_acreditacion is not None and a.ultima_reacreditacion is None:
            ac = models.Acreditacion(
                academico=a,
                fecha=a.user.date_joined,
                comentario='candidato al autoregistrarse al SIGES',
                acreditacion='candidato')
            ac.save()
            ac = models.Acreditacion(
                academico=a,
                fecha=a.fecha_acreditacion,
                comentario=u'acreditación por comité',
                acreditacion=a.acreditacion)
            ac.save()
        elif a.ultima_reacreditacion is not None and a.fecha_acreditacion is None:
            ac = models.Acreditacion(
                academico=a,
                fecha=a.user.date_joined,
                comentario='probablemente acreditado antes del SIGES, candidato al importar datos',
                acreditacion='candidato')
            ac.save()

            ac = models.Acreditacion(
                academico=a,
                fecha=a.ultima_reacreditacion,
                comentario=u'última reacreditación',
                acreditacion=a.acreditacion)
            ac.save()

            # ultima reacreditacion ES la acreditacion
            a.fecha_acreditacion = a.ultima_reacreditacion
            a.save()

    else:
        ac = models.Acreditacion(
            academico=a,
            fecha=a.user.date_joined,
            comentario=u'estado pre-candidato',
            acreditacion=a.acreditacion)
        ac.save()

        # siempre debe tener una fecha
        a.fecha_acreditacion = a.user.date_joined
        a.save()

