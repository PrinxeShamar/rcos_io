"""Django settings for rcos_io project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

from django.contrib.messages import constants as messages
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

import sentry_sdk

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ["ENV"] == "development"


sentry_sdk.init(
    dsn="https://9994829e0309480fb835f3b5eb9e600b@o4504487931346944.ingest.sentry.io/4504487932395520",
    integrations=[
        DjangoIntegration(),
    ],
    environment=os.environ["ENV"],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.75 if DEBUG else 0.25,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "rcos.up.railway.app",
    "rcos-staging.up.railway.app",
    "new.rcos.io",
]

CSRF_TRUSTED_ORIGINS = [
    "https://rcos.up.railway.app",
    "https://rcos-staging.up.railway.app",
    "https://new.rcos.io",
]

PUBLIC_BASE_URL = os.environ["PUBLIC_BASE_URL"]

# Application definition

INSTALLED_APPS = [
    "portal",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "markdownify.apps.MarkdownifyConfig",
    "magiclink",
    "anymail",
    "crispy_forms",
    "crispy_bulma",
    "debug_toolbar",
    # "django_celery_beat"
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bulma",)

CRISPY_TEMPLATE_PACK = "bulma"

CRISPY_CLASS_CONVERTERS = {"numberinput": "input"}
CRISPY_CLASS_CONVERTERS = {"datetime": "input"}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rcos_io.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portal.views.load_semesters",
            ],
        },
    },
]

WSGI_APPLICATION = "rcos_io.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if os.environ["ENV"] == "development":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["PGDATABASE"],
            "USER": os.environ["PGUSER"],
            "PASSWORD": os.environ["PGPASSWORD"],
            "HOST": os.environ["PGHOST"],
            "PORT": os.environ["PGPORT"],
        }
    }

AUTH_USER_MODEL = "portal.User"

AUTHENTICATION_BACKENDS = (
    "magiclink.backends.MagicLinkBackend",
    "django.contrib.auth.backends.ModelBackend",
)

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

CELERY_TIMEZONE = TIME_ZONE

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 2, 592, 000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

INTERNAL_IPS = ["127.0.0.1", "localhost"]

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "em",
            "i",
            "li",
            "ol",
            "p",
            "strong",
            "ul",
        ]
    }
}

GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]

GITHUB_OAUTH_APP_CLIENT_ID = os.environ["GITHUB_OAUTH_APP_CLIENT_ID"]

GITHUB_OAUTH_APP_CLIENT_SECRET = os.environ["GITHUB_OAUTH_APP_CLIENT_SECRET"]

GITHUB_OAUTH_APP_REDIRECT_URL = os.environ["GITHUB_OAUTH_APP_REDIRECT_URL"]

DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]

DISCORD_CLIENT_SECRET = os.environ["DISCORD_CLIENT_SECRET"]

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

DISCORD_SERVER_ID = os.environ["DISCORD_SERVER_ID"]

DISCORD_VERIFIED_ROLE_ID = os.environ["DISCORD_VERIFIED_ROLE_ID"]

DISCORD_REDIRECT_URL = os.environ["DISCORD_REDIRECT_URL"]

DISCORD_PROJECT_PAIRING_CATEGORY_ID = os.environ["DISCORD_PROJECT_PAIRING_CATEGORY_ID"]

DISCORD_PROJECT_LEAD_ROLE_ID = os.environ["DISCORD_PROJECT_LEAD_ROLE_ID"]

LOGIN_URL = "magiclink:login"

MAGICLINK_LOGIN_TEMPLATE_NAME = "portal/magiclink/login.html"

MAGICLINK_LOGIN_SENT_TEMPLATE_NAME = "portal/magiclink/login_sent.html"

MAGICLINK_LOGIN_FAILED_TEMPLATE_NAME = "portal/magiclink/login_failed.html"

MAGICLINK_AUTH_TIMEOUT = 60 * 60 * 24 # 1 day

MAGICLINK_TOKEN_USES = 5

MAGICLINK_REQUIRE_SAME_BROWSER = False

MAGICLINK_REQUIRE_SAME_IP = False

MAGICLINK_REQUIRE_SIGNUP = False  # First login will create user

MAGICLINK_SIGNUP_TEMPLATE_NAME = "magiclink/signup.html"

LOGIN_REDIRECT_URL = "/"

MAGICLINK_SIGNUP_LOGIN_REDIRECT = "/"

DEFAULT_FROM_EMAIL = "no-reply@rcos.io"

SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "anymail.backends.mailjet.EmailBackend"
)

ANYMAIL = {
    "MAILJET_API_KEY": os.environ["MAILJET_API_KEY"],
    "MAILJET_SECRET_KEY": os.environ["MAILJET_SECRET_KEY"],
}

MESSAGE_TAGS = {
    messages.INFO: "is-info",
    messages.DEBUG: "is-light",
    messages.ERROR: "is-danger",
    messages.SUCCESS: "is-success",
    messages.WARNING: "is-warning",
}

if os.environ["ENV"] == "development":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ["REDIS_URL"],
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

CELERY_BROKER_URL = os.environ["REDIS_URL"]
CELERY_RESULT_BACKEND = os.environ["REDIS_URL"]
