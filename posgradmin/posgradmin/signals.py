# coding: utf-8
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from posgradmin.models import Academico, Acreditacion, Curso
from django.db.models.signals import m2m_changed


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


@receiver(post_save, sender=Curso)
def curso_genera_constancias(sender, **kwargs):
    c = kwargs['instance']
    c.genera_constancias()


def curso_academicos_changed(sender, **kwargs):
    if kwargs['action'] == "post_add":
        c = kwargs['instance']
        c.genera_constancias()

m2m_changed.connect(curso_academicos_changed, sender=Curso.academicos.through)



@receiver(post_save, sender=Acreditacion)
def genera_carta_acreditacion(sender, **kwargs):
    ac = kwargs['instance']
    ac.genera_carta()

