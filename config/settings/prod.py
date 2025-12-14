"""
Production settings for Compozy project.

This file contains settings specific to the production environment.
Security and performance optimizations are applied here.
"""

import copy
from .base import *

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: SECRET_KEY must be set via environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable must be set in production')

# ALLOWED_HOSTS must be set in production for security
# Filter out empty strings to prevent security vulnerability
ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ValueError(
        'ALLOWED_HOSTS environment variable must be set in production. '
        'Example: ALLOWED_HOSTS=example.com,www.example.com'
    )

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

if dj_database_url:
    # dj_database_url.config() automatically reads DATABASE_URL from environment
    # The default parameter should only be used for literal fallback strings, not env vars
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError('DATABASE_URL environment variable must be set in production')
    
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback if dj-database-url is not installed
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Simple parsing (will be replaced when dj-database-url is installed)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME', 'compozy'),
                'USER': os.environ.get('DB_USER', 'compozy'),
                'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                'HOST': os.environ.get('DB_HOST', 'localhost'),
                'PORT': os.environ.get('DB_PORT', '5432'),
            }
        }
    else:
        raise ValueError('DATABASE_URL environment variable must be set in production')

# Cache configuration (Redis for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'compozy',
        'TIMEOUT': 300,
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Logging - Production level
# Create a deep copy to avoid mutating the shared LOGGING dict from base.py
LOGGING = copy.deepcopy(LOGGING)
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'

# Celery configuration (will be set up in task 1.4)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))
