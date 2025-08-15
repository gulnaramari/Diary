import os
import sys
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("DEBUG") == "True" else False

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "users.Employee"

# === Apps ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_yasg",
    "users",
    "labbook",
]

# === Middleware (CORS before CommonMiddleware) ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === DRF ===
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # If you add drf-spectacular, enable the next line:
    # "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


def env_required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing env var: {key}")
    return val


if 'test' in sys.argv or 'migrate' in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env_required("POSTGRES_DB"),
            "USER": env_required("POSTGRES_USER"),
            "PASSWORD": env_required("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),  # TCP, НЕ сокет
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }


# === Password validation ===
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === I18N / TZ ===
LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# === Static / Media ===
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # ensure folder exists
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# === Defaults ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# === Auth redirects ===
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "labbook:home"
LOGOUT_REDIRECT_URL = "users:login"

# === Cache (Redis) ===
USE_CACHE = True
if USE_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://redis:6379/1",
        }
    }

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000",
                        "https://read-and-write.example.com", "http://192.168.0.107"]

CORS_ALLOWED_ORIGINS = ["https://example.com", "https://sub.example.com", "http://localhost:8000",
                        "http://127.0.0.1:8000", "http://192.168.0.107"]


CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True
