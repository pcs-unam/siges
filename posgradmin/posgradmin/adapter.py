from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.shortcuts import resolve_url
from datetime import datetime, timedelta

class AccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        threshold = 90 #seconds

        if not hasattr(request.user, 'academico'):
            print "aqui crear perfil academico"

        return resolve_url('/inicio/')
