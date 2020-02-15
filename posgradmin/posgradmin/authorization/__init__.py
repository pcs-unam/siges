def is_staff(user):
    if hasattr(user, 'asistente') \
       or user.is_staff:
        return True
    else:
        return False


def in_program(user):
    if hasattr(user, 'asistente') \
       or hasattr(user, 'estudiante') \
       or hasattr(user, 'academico') \
       or user.is_staff:
        return True
    else:
        return False


def is_academico(user):
    if hasattr(user, 'academico'):
        return True
    else:
        return False


def is_estudiante(user):
    if hasattr(user, 'estudiante'):
        return True
    else:
        return False
