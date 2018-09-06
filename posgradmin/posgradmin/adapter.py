from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.shortcuts import resolve_url
import posgradmin.models as models

class AccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):

        if not hasattr(request.user, 'academico'):
            a = models.Academico(user=request.user,
                                 acreditacion='candidato')
            a.save()

        return resolve_url(settings.APP_PREFIX + '/inicio/')
