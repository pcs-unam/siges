# coding: utf-8

"""
Django settings for posgradmin project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p!v9yqb(jvx2*cq#ir%1gcj6yld07u+c=w53iupn^v!tn_3=#g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'posgradmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'crispy_forms',
    'sortable_listview',
    'django_markdown2'
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'posgradmin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'posgradmin/posgradmin/templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'posgradmin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'es-la'

TIME_ZONE = 'Mexico/General'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = 'Y-m-d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

ACCOUNT_ACTIVATION_DAYS = 2


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

CRISPY_TEMPLATE_PACK = 'bootstrap3'
LOGIN_REDIRECT_URL = '/inicio/'


solicitudes_estados = (
        ("nueva",
         "nueva"),
        ("agendada",
         "agendada"),
        ("atendida",
         "atendida"),
        ("cancelada",
         "cancelada"),
)


solicitudes_profesoriles = (
        ("registrar_catedra",
         "Registrar Cátedra"),
        ("solicitar_apoyo_económico",
         "Solicitar Apoyo Económico"),
    )

solicitudes_tutoriles = (
        ("solicitar_baja_tutor",
         "Solicitar Baja de Tutoría en el Programa"),
        ("avisar_ausencia",
         "Aviso de Ausencia por Sabático u Otra Razón"))

solicitudes_estudiantiles = (
    ("cambio_proyecto",
     "Cambio de título y/o campo de conocimiento de proyecto"),

    ("cambiar_comite_tutoral",
     "Elegir comité tutoral"),

    ('registrar_actividad_complementaria',
     "Registro de actividad complementaria"),
    ('solicitar_candidatura',
     "Solicitud de examen de candidtaura"),

    ('seleccionar_jurado_candidatura',
     "Selección de jurado de candidatura"),
    ('seleccionar_jurado_grado',
     "Selección de jurado de grado"),

    ("reportar_suspension",
     "Reportar suspensión"))

solicitud_otro = (
    ('otro',
     'Otro'),)
