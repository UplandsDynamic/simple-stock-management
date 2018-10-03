import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u%-qma4$u2%%af(84k)a=5x6tw)u#x4tr46+&(8ts!6+vw!t_^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # REMEMBER TO CHANGE TO False IN PRODUCTION!
PRODUCTION = False  # REMEMBER TO CHANGE TO True IN PRODUCTION!

# Network
SITE_FQDN = 'localhost'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
ROOT_URLCONF = 'StockManagement.urls'
WSGI_APPLICATION = 'StockManagement.wsgi.application'
SECURE_SSL_REDIRECT = False if not PRODUCTION else True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stock_control.apps.StockControlConfig',
    'stock_control_frontend.apps.StockControlFrontendConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'webpack_loader'
]

# webpack loader config, for REACT frontend
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'stock_control_frontend/react/webpack-stats.json'),
    }
}

# Rest framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'stock_control.custom_permissions.AccessPermissions',
    ],
    'PAGE_SIZE': 5,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

# Caches
SITE_WIDE_CACHE = True  # site-wide caching system. Set False for more granular control with view & template caching.
DEFAULT_CACHES_TTL = 0  # 0 means equates to 'do not cache'. E.g. to cache for 24 hours: ((60 * 60) * 60) * 24
CACHE_SESSION_SECONDS = 60 * 60

if SITE_WIDE_CACHE:
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = DEFAULT_CACHES_TTL
    CACHE_MIDDLEWARE_KEY_PREFIX = 'stock_management_production_server'
    MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')  # HAS TO GO FIRST IN MIDDLEWARE LIST
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')  # HAS TO GO LAST IN MIDDLEWARE LIST

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

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'stock_control_frontend/static'),
    os.path.join(
        BASE_DIR, 'stock_control_frontend/react/assets')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
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

# Email services
EMAIL_BACKEND = "anymail.backends.sparkpost.EmailBackend"
DEFAULT_FROM_EMAIL = 'me@mydomain.com'
ANYMAIL = {
    'IGNORE_UNSUPPORTED_FEATURES': True,
    'SPARKPOST_API_KEY': 'my_sparkpost_api_key',
    'SPARKPOST_API_URL': 'https://api.eu.sparkpost.com/api/v1',
}

# StockManagement Application
STOCK_MANAGEMENT_OPTIONS = {
    'email': {
        'notifications_on': False if DEBUG else True,
        'notifications_to_transfer_requester': True
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
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
    },
    'loggers': {
        'main': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
