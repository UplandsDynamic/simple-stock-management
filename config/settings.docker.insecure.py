"""
Django settings for StockManagement project.
"""
import os, string, random, locale
from urllib.parse import urlsplit

""" INITIAL PARAMETERS """

# # # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # higher than the count of fields

# # # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', default=0))
# # # GENERATE A NEW UNIQUE SECRET KEY (secret_key.txt) IF DOES NOT ALREADY EXIST
KEY_PATH = os.path.join(BASE_DIR, 'secret_key', 'secret_key.txt')
try:
    with open(KEY_PATH, 'r') as f:
        SECRET_KEY = f.read().strip()
except IOError:
    SECRET_KEY = ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation)
                          for _ in range(50)])
    with open(KEY_PATH, 'w') as f:
        f.write(SECRET_KEY)

""" MAIN CONFIGURATION """

# # # Network
APP_URL = os.environ.get('APP_URL')
ROOT_URLCONF = 'StockManagement.urls'
WSGI_APPLICATION = 'StockManagement.wsgi.application'
X_FRAME_OPTIONS = 'DENY'
# SECURE_HSTS_SECONDS = 3600
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
#  SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = [urlsplit(APP_URL).netloc.split(':')[0]]
# CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (APP_URL,)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# # # Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stock_control.apps.StockControlConfig',
    #'accounts.apps.AccountsConfig',
    #'email_service.apps.EmailServiceConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_q'
]

# # # Rest framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'stock_control.custom_permissions.AccessPermissions',
    ],
    'PAGE_SIZE': 5,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
     # 'DEFAULT_THROTTLE_CLASSES': (
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle'
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '1/second',
    #     'user': '2/second'
    # }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

Q_CLUSTER = {
    'name': 'SimpleStockManagement',
    'daemonize_workers': True,
    'compress': True,
    'workers': 2,
    'recycle': 5000,
    'timeout': None,
    # 'django_redis': 'default',
    'retry': 100000,
    'queue_limit': 4,
    'bulk': 1,
    'orm': 'default',
    'sync': False,  # Set True to debug in sync mode.
    'guard_cycle': 5,
    'cpu_affinity': 1,
    'catch_up': True
}

# # # Caches
USE_REDIS_CACHE = False
SITE_WIDE_CACHE = True  # site-wide caching system. Set False for more granular control with view & template caching.
DEFAULT_CACHES_TTL = 0  # 0 means equates to 'do not cache'. E.g. to cache for 24 hours: ((60 * 60) * 60) * 24
CACHE_SESSION_SECONDS = 60 * 60

if SITE_WIDE_CACHE:
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = DEFAULT_CACHES_TTL  # cache session data for an hour
    CACHE_MIDDLEWARE_KEY_PREFIX = 'stock_management_production_server'
    MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')  # HAS TO GO FIRST IN MIDDLEWARE LIST
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')  # HAS TO GO LAST IN MIDDLEWARE LIST

if not USE_REDIS_CACHE:
    CACHES = {'default':
                  {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                   'TIMEOUT': DEFAULT_CACHES_TTL,
                   'LOCATION': 'stockmanagement-backend-cache'
                   },
              'template_fragments':
                  {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                   'TIMEOUT': DEFAULT_CACHES_TTL,
                   'LOCATION': 'stockmanagement-template-fragments-cache'
                   }
              }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/1',
            'TIMEOUT': DEFAULT_CACHES_TTL,  # default TTL for the cache in sects(e.g. 5 mins = 'TIMEOUT': 60 * 5)
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            },
            'KEY_PREFIX': 'stock_management_production_server'
        },
        'sessions': {  # used by SESSION_CACHE_ALIAS, below
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/3',
            'TIMEOUT': CACHE_SESSION_SECONDS,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            },
            'KEY_PREFIX': 'stock_management_production_server'
        },
        'template_fragments': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/4',
            'TIMEOUT': DEFAULT_CACHES_TTL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            },
            'KEY_PREFIX': 'stock_management_production_server'
        },
    }

# # # Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('SQL_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}

STATICFILES_DIRS = []
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# # # Password validation
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

# # # Email services
EMAIL_BACKEND = "anymail.backends.sparkpost.EmailBackend"
DEFAULT_FROM_EMAIL = 'productions@staging.aninstance.com'
ANYMAIL = {
    'IGNORE_UNSUPPORTED_FEATURES': True,
    'SPARKPOST_API_KEY': 'my_api_key',
    'SPARKPOST_API_URL': 'https://api.eu.sparkpost.com/api/v1',
}

# # # StockManagement Application
STOCK_MANAGEMENT_OPTIONS = {
        'email': {
            'notifications_on': True,
            'notifications_to_transfer_requester': True,
            'notifications_to_administrators': True,
        }
    }

# # # Internationalization
locale.setlocale(locale.LC_ALL)  # set locale
LANGUAGE_CODE = (os.environ.get('LANGUAGE_CODE'))  # set language code
# LOCALE_PATHS = (
#     os.path.join(BASE_DIR, 'locale'),
# )
# LANGUAGES = (
#     ('en', 'English')
# )
TIME_ZONE = os.environ.get('TIME_ZONE')
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True 
USE_TZ = True

# Logging
LOG_FILE = '/var/log/ssm.log'  # production

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_q': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}