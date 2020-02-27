# coding: utf-8
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from posgradmin.models import Academico, Acreditacion


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
    
    a.copia_ultima_acreditacion()
    

@receiver(post_save, sender=Acreditacion)
def copia_acreditacion_a_academico(sender, **kwargs):
    ac = kwargs['instance']
    ac.academico.copia_ultima_acreditacion()
    ac.academico.save()


