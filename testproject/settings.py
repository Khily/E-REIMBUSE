"""
Django settings for testproject project.
"""

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-cs&yh(1i5c5%lvrbfqcneg2x5dex0xxqxej&q2y*!8iqx&*&$4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*.onrender.com', '127.0.0.1', 'localhost']


# Application definition
INSTALLED_APPS = [
    # Default Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize', # Untuk format angka (Rp)

    # Third-party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_extensions',

    # Local Apps
    'core_app.apps.CoreAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'testproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Path ke folder templates Anda
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

WSGI_APPLICATION = 'testproject.wsgi.application'


# Database Configuration
# Use DATABASE_URL if available (for production), otherwise use local PostgreSQL
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production database configuration (Render)
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Local development database configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'reimbursement_bbm',
            'USER': 'postgres',
            'PASSWORD': 'Nafisah1234.',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

# Custom User Model & Auth
AUTH_USER_MODEL = 'core_app.CustomUser'
AUTHENTICATION_BACKENDS = [
    'core_app.backends.PersonalNumberBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation (Dikosongkan untuk development)
AUTH_PASSWORD_VALIDATORS = []


# Internationalization
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files collection for production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configure WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Konfigurasi Pihak Ketiga
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_MODEL_USERNAME_FIELD': 'personal_number',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# URL Halaman Login
LOGIN_URL = 'home'
