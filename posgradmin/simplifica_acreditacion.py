"""
pipe me into ./manage.py shell
"""
import posgradmin.models as models

for a in models.Academico.objects.exclude(acreditacion='no acreditado'):
    a.acreditacion = a.acreditacion[-1]
    a.save()
