# coding: utf8

from django.contrib.auth.models import User

from posgradmin.models import Estudiante, Entidad, Proyecto, \
    CampoConocimiento

import csv


def load(f, ingreso, semestre):
    reader = csv.DictReader(f)

    errores = []
    for row in reader:
        # "cuenta"-,"nombre"-,"correo"-,"plan"-,"proyecto"-,"campo"-,"entidad"-
        u = User(username=str(row['cuenta']),
                 email=row['correo'])
        u.name = row['nombre']
        u.save()

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
