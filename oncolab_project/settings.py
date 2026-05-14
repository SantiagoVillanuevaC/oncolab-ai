"""
Django settings para OncoLab AI
Proyecto Final Universitario — Diagnóstico Médico Asistido por IA
"""

from pathlib import Path

# Directorio raíz del proyecto (donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta — en producción cámbiala por una segura
SECRET_KEY = 'django-oncolab-ai-proyecto-universitario-key-2024'

# En producción cambia a False
DEBUG = True

ALLOWED_HOSTS = ['*']

# ─── Aplicaciones instaladas ─────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',   # Nuestra app principal
]

# ─── Middleware ───────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oncolab_project.urls'

# ─── Templates ───────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,   # Django busca en core/templates/ automáticamente
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

WSGI_APPLICATION = 'oncolab_project.wsgi.application'

# ─── Base de datos (SQLite por defecto) ──────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── Sesiones (necesarias para guardar diagnósticos temporalmente) ────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 horas

# ─── Internacionalización ─────────────────────────────────────────────
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ─── Archivos estáticos ───────────────────────────────────────────────
STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Logging para ver mensajes del modelo en consola ─────────────────
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
