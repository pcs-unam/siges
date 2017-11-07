from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User

from posgradmin.models import Perfil, Estudiante, Entidad, Proyecto

import csv


def load(f, ingreso_year, semestre):
    reader = csv.DictReader(f)

    for row in reader:
        u = User(name=row['nombre'])
        u.save()

        e = Estudiante()
        e.user=u
        e.save()

        # etc.
