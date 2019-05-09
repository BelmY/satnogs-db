import sentry_sdk
from decouple import Csv, config
from dj_database_url import parse as db_url
from sentry_sdk.integrations.django import DjangoIntegration
from unipath import Path

ROOT = Path(__file__).parent

ENVIRONMENT = config('ENVIRONMENT', default='dev')
DEBUG = config('DEBUG', default=True, cast=bool)
AUTH0 = config('AUTH0', default=False, cast=bool)

# Apps
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'avatar',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'compressor',
    'csp',
)
LOCAL_APPS = (
    'db.base',
    'db.api',
)

if AUTH0:
    THIRD_PARTY_APPS += ('social_django', )
    LOCAL_APPS += ('auth0login', )

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middlware
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
)

# Email
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=300, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@satnogs.org')
ADMINS = [('SatNOGS Admins', DEFAULT_FROM_EMAIL)]
MANAGERS = ADMINS
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Cache
CACHES = {
    'default': {
        'BACKEND':
        config('CACHE_BACKEND', default='django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': config('CACHE_LOCATION', default='unique-location'),
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
            'CLIENT_CLASS': config('CACHE_CLIENT_CLASS', default=''),
        },
        'KEY_PREFIX': 'db-{0}'.format(ENVIRONMENT),
    }
}
CACHE_TTL = config('CACHE_TTL', default=300, cast=int)

# Internationalization
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            Path(ROOT).child('templates').resolve(),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'db.base.context_processors.analytics', 'db.base.context_processors.stage_notice',
                'db.base.context_processors.auth_block', 'db.base.context_processors.logout_block',
                'db.base.context_processors.version', 'db.base.context_processors.decoders_version'
            ],
            'loaders': [
                (
                    'django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]
                ),
            ],
        },
    },
]

# Static & Media
STATIC_ROOT = config('STATIC_ROOT', default=Path('staticfiles').resolve())
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    Path(ROOT).child('static').resolve(),
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
MEDIA_ROOT = config('MEDIA_ROOT', default=Path('media').resolve())
MEDIA_URL = '/media/'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
SATELLITE_DEFAULT_IMAGE = '/static/img/sat.png'
COMPRESS_ENABLED = config('COMPRESS_ENABLED', default=False, cast=bool)
COMPRESS_OFFLINE = config('COMPRESS_OFFLINE', default=False, cast=bool)
COMPRESS_CACHE_BACKEND = config('COMPRESS_CACHE_BACKEND', default='default')
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.rCSSMinFilter'
]

# App conf
ROOT_URLCONF = 'db.urls'
WSGI_APPLICATION = 'db.wsgi.application'

# Auth
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )
if AUTH0:
    AUTHENTICATION_BACKENDS += ('auth0login.auth0backend.Auth0', )

ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
LOGIN_REDIRECT_URL = 'home'
if AUTH0:
    LOGIN_URL = '/login/auth0'
    LOGOUT_REDIRECT_URL = 'https://' + config('SOCIAL_AUTH_AUTH0_DOMAIN') + \
                          '/v2/logout?returnTo=' + config('SITE_URL')
else:
    LOGIN_URL = 'account_login'
    LOGOUT_REDIRECT_URL = '/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s - %(process)d %(thread)d - %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'db': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}

# Sentry
SENTRY_ENABLED = config('SENTRY_ENABLED', default=False, cast=bool)
if SENTRY_ENABLED:
    sentry_sdk.init(dsn=config('SENTRY_DSN', default=''), integrations=[DjangoIntegration()])

# Celery
CELERY_ENABLE_UTC = USE_TZ
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_RESULTS_EXPIRES = 3600
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_ALWAYS_EAGER = False
CELERY_DEFAULT_QUEUE = 'db-{0}-queue'.format(ENVIRONMENT)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': config('REDIS_VISIBILITY_TIMEOUT', default=604800, cast=int),
    'fanout_prefix': True
}
REDIS_CONNECT_RETRY = True

# API
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':
    ('rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly', ),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication', ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', )
}

# Security
SECRET_KEY = config('SECRET_KEY', default='changeme')
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
CSP_DEFAULT_SRC = (
    "'self'",
    'https://*.mapbox.com',
)
CSP_SCRIPT_SRC = (
    "'self'",
    'https://*.google-analytics.com',
    "'unsafe-eval'",
)
CSP_IMG_SRC = (
    "'self'",
    'https://*.gravatar.com',
    'https://*.mapbox.com',
    'https://*.google-analytics.com',
    'data:',
    'blob:',
)
CSP_CHILD_SRC = ('blob:', )
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

# Database
DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
DATABASES = {'default': db_url(DATABASE_URL)}

# NETWORK API
NETWORK_API_ENDPOINT = config('NETWORK_API_ENDPOINT', default='https://network.satnogs.org/api/')
DATA_FETCH_DAYS = config('DATA_FETCH_DAYS', default=10, cast=int)

# Mapbox API
MAPBOX_GEOCODE_URL = 'https://api.tiles.mapbox.com/v4/geocode/mapbox.places/'
MAPBOX_TOKEN = config('MAPBOX_TOKEN', default='')

# Influx DB for decoded data_id
USE_INFLUX = config('USE_INFLUX', default=False, cast=bool)
INFLUX_HOST = config('INFLUX_HOST', default='localhost')
INFLUX_PORT = config('INFLUX_PORT', default='8086')
INFLUX_USER = config('INFLUX_USER', default='db')
INFLUX_PASS = config('INFLUX_PASS', default='db')
INFLUX_DB = config('INFLUX_DB', default='db')
INFLUX_SSL = config('INFLUX_SSL', default=False, cast=bool)

if AUTH0:
    SOCIAL_AUTH_TRAILING_SLASH = False  # Remove end slash from routes
    SOCIAL_AUTH_AUTH0_DOMAIN = config('SOCIAL_AUTH_AUTH0_DOMAIN', default='YOUR_AUTH0_DOMAIN')
    SOCIAL_AUTH_AUTH0_KEY = config('SOCIAL_AUTH_AUTH0_KEY', default='YOUR_CLIENT_ID')
    SOCIAL_AUTH_AUTH0_SECRET = config('SOCIAL_AUTH_AUTH0_SECRET', default='YOUR_CLIENT_SECRET')
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'first_name', 'last_name']

    SOCIAL_AUTH_PIPELINE = (
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.social_auth.associate_by_email',
        'social_core.pipeline.user.get_username',
        'social_core.pipeline.user.create_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
        'social_core.pipeline.user.user_details',
    )

    SOCIAL_AUTH_AUTH0_SCOPE = [
        'openid',
        'email',
        'profile',
    ]

if ENVIRONMENT == 'dev':
    # Disable template caching
    for backend in TEMPLATES:
        del backend['OPTIONS']['loaders']
        backend['APP_DIRS'] = True
