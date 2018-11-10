# coding: utf-8
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from posgradmin.models import Perfil, Academico
import os.path


@receiver(pre_save, sender=Academico)
def academico_verifica_resumen_perfil(sender, **kwargs):
    u"""
    perfil academico actualiza su estado de compleción
    """
    a = kwargs['instance']
    a.resumen_completo = a.verifica_resumen()
    a.perfil_personal_completo = a.verifica_perfil_personal()

    print a.verifica_perfil_personal()
