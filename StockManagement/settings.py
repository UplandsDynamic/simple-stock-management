"""
Django settings for StockManagement project.

REMEMBER, BEFORE PRODUCTION RUN SECURITY CHECKS:

    python manage.py check --deploy

"""

import os, string, random

""" INITIAL PARAMETERS """

# # # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # this setting will be OVERRIDDEN according tot the RUN_TYPE defined below.

# # # RUN TYPE: Define run type of the application, as read from run_type.txt file in project root
RUN_TYPE_PATH = os.path.join(BASE_DIR, 'run_type.txt')
RUN_TYPE_OPTIONS = ['DEVEL', 'STAGING', 'PRODUCTION']
RUN_TYPE = RUN_TYPE_OPTIONS[0]
try:
    with open(RUN_TYPE_PATH, 'r') as f:
        RT = f.read().strip()
        RUN_TYPE = RT if RT in RUN_TYPE_OPTIONS else RUN_TYPE
except IOError:
    RUN_TYPE = RUN_TYPE_OPTIONS[0]  # DEVEL as default
    with open(RUN_TYPE_PATH, 'w') as f:
        f.write(RUN_TYPE_OPTIONS[0])

# # # GENERATE A NEW UNIQUE SECRET KEY (secret_key.txt) IF DOES NOT ALREADY EXIST
KEY_PATH = os.path.join(BASE_DIR, 'secret_key.txt')
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
WORKING_URL = ''
ROOT_URLCONF = 'StockManagement.urls'
WSGI_APPLICATION = 'StockManagement.wsgi.application'
X_FRAME_OPTIONS = 'DENY'
# SECURE_HSTS_SECONDS = 3600
if RUN_TYPE == 'DEVEL' or not RUN_TYPE:
    DEBUG = True
    WORKING_URL = 'localhost'
    WORKING_PORT = '3000'
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_BROWSER_XSS_FILTER = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ALLOWED_HOSTS = [WORKING_URL]
    # CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = (WORKING_URL, 'localhost:3001')
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
elif RUN_TYPE == 'STAGING':
    DEBUG = False
    WORKING_URL = 'sm.staging.aninstance.com'
    WORKING_PORT = '443'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    #  SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    ALLOWED_HOSTS = [WORKING_URL]
    # CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = (WORKING_URL,)
    STATIC_ROOT = os.path.join('/var/www/django/'
                               'sm.staging.aninstance.com/static')
    MEDIA_ROOT = os.path.join('/var/www/django/'
                              'sm.staging.aninstance.com/media')
elif RUN_TYPE == 'PRODUCTION':
    DEBUG = False
    WORKING_URL = 'sm.my.domain.com'
    WORKING_PORT = '443'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    #  SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    ALLOWED_HOSTS = [WORKING_URL]
    # CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = (WORKING_URL,)
    STATIC_ROOT = os.path.join('/var/www/django/'
                               'sm.my.domain.com/static')
    MEDIA_ROOT = os.path.join('/var/www/django/'
                              'sm.my.domain.com/media')

# # # Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stock_control.apps.StockControlConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
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
    )
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
if RUN_TYPE == RUN_TYPE_OPTIONS[2]:  # production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'my_db_name',
            'USER': 'my_db_user',
            'PASSWORD': 'my_db_password',
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
elif RUN_TYPE == RUN_TYPE_OPTIONS[1]:  # staging
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'stockmanagement',
            'USER': 'stockmanagement',
            'PASSWORD': 'a_ReAllY-bAd-pw',
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'stock_control_frontend/static'),
]
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
if RUN_TYPE == RUN_TYPE_OPTIONS[2]:  # production
    EMAIL_BACKEND = "anymail.backends.sparkpost.EmailBackend"
    DEFAULT_FROM_EMAIL = 'stockmanagement@sm.my.domain.com'
    ANYMAIL = {
        'IGNORE_UNSUPPORTED_FEATURES': True,
        'SPARKPOST_API_KEY': 'my_api_key',
        'SPARKPOST_API_URL': 'https://api.eu.sparkpost.com/api/v1',
    }
else:  # staging or devel
    EMAIL_BACKEND = "anymail.backends.sparkpost.EmailBackend"
    DEFAULT_FROM_EMAIL = 'productions@staging.aninstance.com'
    ANYMAIL = {
        'IGNORE_UNSUPPORTED_FEATURES': True,
        'SPARKPOST_API_KEY': 'my_api_key',
        'SPARKPOST_API_URL': 'https://api.eu.sparkpost.com/api/v1',
    }

# # # StockManagement Application
STOCK_MANAGEMENT_OPTIONS = {
    RUN_TYPE_OPTIONS[0]: {  # devel
        'email': {
            'notifications_on': False,
            'notifications_to_transfer_requester': True,
            'notifications_to_administrators': True,
        }
    },
    RUN_TYPE_OPTIONS[1]: {  # staging
        'email': {
            'notifications_on': False,
            'notifications_to_transfer_requester': True,
            'notifications_to_administrators': True,
        }
    },
    RUN_TYPE_OPTIONS[2]: {  # production
        'email': {
            'notifications_on': True,
            'notifications_to_transfer_requester': True,
            'notifications_to_administrators': True,
        }
    },
}

# # # Internationalization
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
LANGUAGE_CODE = 'en-gb'
# LANGUAGES = (
#     ('en', 'English')
# )
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
LOG_FILE = {
    RUN_TYPE_OPTIONS[0]: '/var/log/django/ssm.devel.log',  # devel
    RUN_TYPE_OPTIONS[1]: '/var/log/django/ssm.staging.log',  # staging
    RUN_TYPE_OPTIONS[2]: '/var/log/django/ssm.prod.log',  # production
}

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE[RUN_TYPE],
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'main': {
            'handlers': ['file'] if RUN_TYPE == RUN_TYPE_OPTIONS[1] or RUN_TYPE == RUN_TYPE_OPTIONS[2] else ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'] if RUN_TYPE == RUN_TYPE_OPTIONS[1] or RUN_TYPE == RUN_TYPE_OPTIONS[2] else ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
