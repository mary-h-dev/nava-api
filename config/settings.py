
from datetime import timedelta
from corsheaders.defaults import default_methods
import locale
import os
import dj_database_url
from pathlib import Path
import environ
from dotenv import load_dotenv
load_dotenv()


AUTH_USER_MODEL = 'accounts.User'

BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = "django-insecure-$-6!wh_&rp4+thd2okhke115=6+#pcp22owdtz@m*ii)l#o1tz"


DEBUG = True



SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {         
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },

    'SUPPORTED_SUBMIT_METHODS': [],
}




# ALLOWED_IPS = [
#     "127.0.0.1",    
#     "192.168.1.10",
#     "203.0.113.1" ,  
# ]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #app
    'accounts',
    'blog',
    'treatment_doc',
    'doctors',
    'questions',
    'Panel_Admin',
    'finance',
    'cart',
    'tag',
    'site_info',
    'filemanager',
    'vlog',
    'appointment',
    'podcast',
    # 'landing_manager',
    'Psychological_test',
    'Psychology_workshops',
    #installations
    'rest_framework',
    'rest_framework_simplejwt',
    'djoser',
    'drf_yasg',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'mail_templated',
    'jalali_date',
    'django_celery_results',
    'multiselectfield',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    # "landing_manager.api.v1.middleware.RestrictIPMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
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


WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'railway',
#         'USER': 'postgres',
#         'PASSWORD': os.getenv('PG_PASSWORD'),
#         'HOST': os.getenv('PG_HOST'),
#         'PORT': os.getenv('PG_PORT'),  
#     }
# }


DATABASES = {
    'default': dj_database_url.config(default=os.getenv("DATABASE_URL"))
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True




STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATIC_ROOT = os.path.join(BASE_DIR, "static")
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
#media root
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")



DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',

    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'config.render.CustomJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'otp_login': '3/minute',
    }
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

}

SMS_API_KEY = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'
SMS_LINE = '90009809'




ALLOWED_HOSTS = ['*']


CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "dnt",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


CORS_ALLOWED_ORIGIN_REGEXES = [r"^https?:\/\/localhost:3000$"]

CORS_ALLOW_METHODS = [*default_methods, "DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT",  "POKE"]




# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'honestboy.lme@gmail.com'
# EMAIL_HOST_PASSWORD = 'qjzsiggfjsypybsn'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False


SITE_ID = 1



# CELERY settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# روی لوکال Redis معمولاً روی localhost:6379 اجرا می‌شه
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_BACKEND', 'redis://localhost:6379/0')


# Cache برای Django با Redis لوکال
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://localhost:6379/2",  
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


