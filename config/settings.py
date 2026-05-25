
from pathlib import Path
from datetime import timedelta
import os

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "replace_me_in_prod")
DEBUG = False

ALLOWED_HOSTS = [
    'dreamhouse05.com',
    'www.dreamhouse05.com',
    'api.dreamhouse05.com',
    'admin.dreamhouse05.com',
    'localhost',
    '127.0.0.1',
    '188.120.245.100',
]

# --- Applications ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'corsheaders',

    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',

    'users',
    'cards',
    'developers',
    'notifications',
    'crm',
]

# --- Middleware ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URLS & WSGI ---
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# --- Custom User ---
AUTH_USER_MODEL = "users.User"

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# --- Database ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dreamhouse_db",
        "USER": "dreamuser",
        "PASSWORD": "21012005",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# --- Swagger ---
SPECTACULAR_SETTINGS = {
    "TITLE": "API FOR Dream House",
    "DESCRIPTION": "API для Dream House",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    # Allow request bodies for DELETE so OTP can be passed in docs
    "ALLOWED_METHODS_WITH_BODY": ["PUT", "POST", "PATCH", "DELETE"],
}

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'accept',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "https://dreamhouse05.com",
    "https://www.dreamhouse05.com",
    "https://api.dreamhouse05.com",
    "https://admin.dreamhouse05.com",
]

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'users.backends.PhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# --- Localization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static / Media ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- JWT ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# --- SMS ---
SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'smsru')
P1SMS_API_KEY = os.environ.get('P1SMS_API_KEY', '')
SMSRU_API_ID = os.environ.get(
    'SMSRU_API_ID',
    '73CF6BC6-704B-5E02-91A4-0E762C179A22'
)
SEND_REAL_SMS = os.environ.get('SEND_REAL_SMS', 'False').lower() == 'true'
SMS_DEBUG_RETURN_OTP = os.environ.get('SMS_DEBUG_RETURN_OTP', 'False').lower() == 'true'

# --- Push Notifications ---
# Firebase (Android)
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', None)

# APNs (iOS)
APNS_KEY_PATH = os.environ.get('APNS_KEY_PATH', None)  # Путь к .p8 файлу
APNS_KEY_ID = os.environ.get('APNS_KEY_ID', None)       # Key ID из Apple Developer
APNS_TEAM_ID = os.environ.get('APNS_TEAM_ID', None)     # Team ID из Apple Developer
APNS_BUNDLE_ID = os.environ.get('APNS_BUNDLE_ID', None) # Bundle ID приложения
APNS_USE_SANDBOX = os.environ.get('APNS_USE_SANDBOX', 'True').lower() == 'true'

# --- Logging ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# --- Channels (WebSocket) ---
CHANNEL_LAYERS = {
    "default": {
        # Для продакшена использовать Redis:
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "CONFIG": {"hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379")]},
        # Для разработки — in-memory:
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# --- CRM / Telegram Bot ---
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'change_me_webhook_secret')
BOT_API_SECRET = os.environ.get('BOT_API_SECRET', 'change_me_bot_secret')
BOT_NOTIFY_URL = os.environ.get('BOT_NOTIFY_URL', 'http://127.0.0.1:8001')
