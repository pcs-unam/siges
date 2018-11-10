from django.apps import AppConfig





class posgradminConfig(AppConfig):

    name = u'posgradmin'
    verbose_name = 'Gestor de Posgrado'

    def ready(self):
        import posgradmin.signals
