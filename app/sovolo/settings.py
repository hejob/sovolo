"""
Django settings for sovolo project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

##
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h+7tnng9qb&$^@qa=y_@g5wr0d@6vsq!pa5gwa6e7_8ngj+8k!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['local.domain.jp']


# Application definition

INSTALLED_APPS = [
    'django_gulp',
    'event.apps.EventConfig',
    'tag.apps.TagConfig',
    'user.apps.UserConfig',
    'base.apps.BaseConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'bootstrap3',
    'crispy_forms',
    'social_django',
]

BOOTSTRAP3 = {
    'include_jquery': False,
    'jquery_url': '/static/js/jquery.js',
    'base_url': '/static',
    'css_url': '/static/css/bootstrap-custom.css',
    'javascript_url': '/static/js/bootstrap.js',
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MESSAGE_TAGS = {
    message_constants.ERROR: 'alert alert-danger',
    message_constants.INFO: 'alert alert-info',
    message_constants.SUCCESS: 'alert alert-success',

}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sovolo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]


WSGI_APPLICATION = 'sovolo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sovolo',
        'USER': 'sovolo_admin',
        'PASSWORD': os.environ.get('DATABASE_PASSWORD') or 'pass',
        'HOST': '127.0.0.1',
        'PORT': '5432',
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

LANGUAGES = (
    ('en-us', _('English')),
    ('ja-jp', '日本語'),
)
LANGUAGE_CODE = 'ja-jp'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use
# a trailing slash.
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/user/login/'

AUTH_USER_MODEL = 'user.User'

AUTHENTICATION_BACKENDS = [
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'user.social_auth.require_email',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'user.social_auth.get_profile_image',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'ja_JP',
    'fields': 'id, name, email, age_range'
}

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND',
                               'django.core.mail.backends.console.EmailBackend')

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
DEFAULT_FROM_EMAIL = 'Sovol <noreply@sovol.earth>'

GOOGLE_RECAPTCHA_SECRET = os.environ.get('GOOGLE_RECAPTCHA_SECRET')
GOOGLE_MAP_KEY = os.environ.get('GOOGLE_MAP_KEY')

PREFECTURES = {
    "Hokkaido"  : (_("Hokkaido" ),  1),
    "Aomori"    : (_("Aomori"   ),  2),
    "Iwate"     : (_("Iwate"    ),  3),
    "Miyagi"    : (_("Miyagi"   ),  4),
    "Akita"     : (_("Akita"    ),  5),
    "Yamagata"  : (_("Yamagata" ),  6),
    "Fukushima" : (_("Fukushima"),  7),
    "Ibaraki"   : (_("Ibaraki"  ),  8),
    "Tochigi"   : (_("Tochigi"  ),  9),
    "Gunnma"    : (_("Gunnma"   ), 10),
    "Saitama"   : (_("Saitama"  ), 11),
    "Chiba"     : (_("Chiba"    ), 12),
    "Tokyo"     : (_("Tokyo"    ), 13),
    "Kanagawa"  : (_("Kanagawa" ), 14),
    "Niigata"   : (_("Niigata"  ), 15),
    "Toyama"    : (_("Toyama"   ), 16),
    "Ishikawa"  : (_("Ishikawa" ), 17),
    "Fukui"     : (_("Fukui"    ), 18),
    "Yamanashi" : (_("Yamanashi"), 19),
    "Nagano"    : (_("Nagano"   ), 20),
    "Gifu"      : (_("Gifu"     ), 21),
    "Shizuoka"  : (_("Shizuoka" ), 22),
    "Aichi"     : (_("Aichi"    ), 23),
    "Mie"       : (_("Mie"      ), 24),
    "Shiga"     : (_("Shiga"    ), 25),
    "Kyoto"     : (_("Kyoto"    ), 26),
    "Osaka"     : (_("Osaka"    ), 27),
    "Hyogo"     : (_("Hyogo"    ), 28),
    "Nara"      : (_("Nara"     ), 29),
    "Wakayama"  : (_("Wakayama" ), 30),
    "Tottori"   : (_("Tottori"  ), 31),
    "Shimane"   : (_("Shimane"  ), 32),
    "Okayama"   : (_("Okayama"  ), 33),
    "Hiroshima" : (_("Hiroshima"), 34),
    "Yamaguchi" : (_("Yamaguchi"), 35),
    "Tokushima" : (_("Tokushima"), 36),
    "Kagawa"    : (_("Kagawa"   ), 37),
    "Ehime"     : (_("Ehime"    ), 38),
    "Kouchi"    : (_("Kouchi"   ), 39),
    "Fukuoka"   : (_("Fukuoka"  ), 40),
    "Saga"      : (_("Saga"     ), 41),
    "Nagasaki"  : (_("Nagasaki" ), 42),
    "Kumamoto"  : (_("Kumamoto" ), 43),
    "Ooita"     : (_("Ooita"    ), 44),
    "Miyazaki"  : (_("Miyazaki" ), 45),
    "Kagoshima" : (_("Kagoshima"), 46),
    "Okinawa"   : (_("Okinawa"  ), 47),
}

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

GULP_PRODUCTION_COMMAND='gulp default --production'
