"""
Django settings for task_manager project (development-friendly).

Notes:
- DEBUG=True for local development. Switch to DEBUG=False for production.
- Uses environment variables for database, DEBUG, secret key, email.
- Timezone set to Asia/Kolkata.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Base Directory + Load .env
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------
# Core settings
# ---------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-replace-this-in-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") != "0"

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
).split(",")

# ---------------------------------------------------------------------
# Installed apps
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your app
    "tasks",
]

# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "task_manager.urls"

# ---------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "task_manager.wsgi.application"

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", BASE_DIR / "db.sqlite3"),
    }
}

# ---------------------------------------------------------------------
# Auth & Password validation
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "tasks.CustomUser"

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "tasks" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------
# Authentication redirect settings
# ---------------------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/admin_dashboard/"
LOGOUT_REDIRECT_URL = "/"

# ---------------------------------------------------------------------
# Sessions & CSRF
# ---------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False    # Set True in prod
CSRF_COOKIE_SECURE = False       # Set True in prod
SESSION_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------
# EMAIL SETTINGS (FIXED)
# ---------------------------------------------------------------------
# Default backend for development: prints to console
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "sayakmondal403@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "mqyumwjxdoriskgh")  # Gmail App Password

EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False") == "True"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": os.environ.get(
            "DJANGO_CACHE_BACKEND",
            "django.core.cache.backends.locmem.LocMemCache"
        ),
        "LOCATION": "unique-snowflake",
    }
}

# ---------------------------------------------------------------------
# OTP Settings
# ---------------------------------------------------------------------
OTP_TTL_SECONDS = int(os.environ.get("OTP_TTL_SECONDS", 300))
MAX_OTP_ATTEMPTS = int(os.environ.get("MAX_OTP_ATTEMPTS", 5))

# ---------------------------------------------------------------------
# Rate Limits
# ---------------------------------------------------------------------
RATE_LIMIT = {
    "LOGIN_ATTEMPTS": int(os.environ.get("RATE_LIMIT_LOGIN_ATTEMPTS", 5)),
    "LOGIN_WINDOW": int(os.environ.get("RATE_LIMIT_LOGIN_WINDOW", 300)),
    "PAGE_REQUESTS": int(os.environ.get("RATE_LIMIT_PAGE_REQUESTS", 20)),
    "PAGE_WINDOW": int(os.environ.get("RATE_LIMIT_PAGE_WINDOW", 60)),
}

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.request": {"handlers": ["console"], "level": "ERROR"},
        "django.core.mail": {"handlers": ["console"], "level": "DEBUG"},
    },
}
# ---------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ADMINS = []   # example: [("Sayak", "sayakmondal403@gmail.com")]

# ---------------------------------------------------------------------
# Security Headers
# ---------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
