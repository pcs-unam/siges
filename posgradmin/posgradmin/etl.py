# coding: utf8

from django.contrib.auth.models import User

from posgradmin.models import Estudiante, Entidad, Proyecto, \
    CampoConocimiento

import csv


def load(f, ingreso, semestre):
    reader = csv.DictReader(f)

    errores = []
    for row in reader:
        try:
            u = User(username=str(row['cuenta']),
                     email=row['correo'])
            u.first_name = row['nombre']
            u.last_name = row['apellidos']
            u.password = u'pbkdf2_sha256$36000$wAcW7cBkfTcw$AmKBje123fdSHcvz/3PpchHJ+BEcOBe9km1exOvL+123'
            u.save()
        except:
            row['error'] = 'Imposible crear usuario'
            errores.append(row)
            break

        entidad, creada = Entidad.objects.get_or_create(nombre=row["entidad"])
        if creada:
            row['error'] = 'Entidad creada, posible error de captura'
            errores.append(row)

        e = Estudiante(cuenta=row['cuenta'],
                       plan=row['plan'],
                       entidad=entidad,
                       ingreso=ingreso,
                       semestre=semestre,
                       user=u)
        e.save()

        campo, creado = CampoConocimiento.objects.get_or_create(
            nombre=row["campo"])
        if creado:
            row['error'] = 'Campo de Conocimiento creado, ¿error de captura?'
            errores.append(row)

        p = Proyecto(nombre=row['proyecto'],
                     campo_conocimiento=campo,
                     estudiante=e,
                     aprobado=True)
        p.save()

    return errores
