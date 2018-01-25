from django.conf import settings


def app_prefix(request):
    return {
        'APP_PREFIX': settings.APP_PREFIX,
    }
