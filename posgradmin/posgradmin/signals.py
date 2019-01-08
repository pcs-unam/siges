# coding: utf-8
from django.db.models.signals import pre_save
from django.dispatch import receiver
from posgradmin.models import Academico


@receiver(pre_save, sender=Academico)
def academico_verifica_resumen_perfil(sender, **kwargs):
    u"""
    perfil academico actualiza su estado de compleción
    """
    a = kwargs['instance']
    a.resumen_completo = a.verifica_resumen()
    a.perfil_personal_completo = a.verifica_perfil_personal()

    a.semaforo_maestria = a.verifica_semaforo_maestria()
    a.semaforo_doctorado = a.verifica_semaforo_doctorado()
    
