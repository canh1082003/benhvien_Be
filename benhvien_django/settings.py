"""
Django settings for benhvien_django project.
Supports both local development and Render production via environment variables.
"""

import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Security - read from env in production, fallback for local dev
SECRET_KEY = os.environ.get('SECRET_KEY', 'benhvien-secret-key-change-in-production-2026')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'corsheaders',
    # Local apps
    'core',
    'api',
    'assets_app',
    'locations_app',
    'maintenance_app',
    'inventory_app',
    'documents_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RedirectToReactMiddleware',
]

ROOT_URLCONF = 'benhvien_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'benhvien_django.wsgi.application'

# Database
# Supports 3 configurations in priority order:
# 1. DATABASE_URL env var (single connection string)
# 2. Individual HOST/NAME/USER/PASSWORD/PORT env vars (set manually on Render)
# 3. Local dev fallback (localhost:3800)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
elif os.environ.get('HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('NAME', 'benhvien'),
            'USER': os.environ.get('USER', 'postgres'),
            'PASSWORD': os.environ.get('PASSWORD', 'conganh123'),
            'HOST': os.environ.get('HOST', 'localhost'),
            'PORT': os.environ.get('PORT', '3800'),
        }
    }
else:
    # Local development database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'benhvien',
            'USER': 'postgres',
            'PASSWORD': 'conganh123',
            'HOST': 'localhost',
            'PORT': '3800',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'core.User'

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files - WhiteNoise serves them in production
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS - allow React frontend
CORS_ALLOWED_ORIGINS_ENV = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if CORS_ALLOWED_ORIGINS_ENV:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in CORS_ALLOWED_ORIGINS_ENV.split(',')]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Allow all origins temporarily (set CORS_ALLOWED_ORIGINS env var on Render after Vercel deploy)
    CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# Redirect login to React
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
LOGIN_URL = f'{FRONTEND_URL}/login'
