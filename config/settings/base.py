"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
from environs import Env
from pathlib import Path
import os

from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env.read_env()

POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-7ljcff0x1vz2$y)7byy!3!&ys1%f(wfu*zkwb)twdt%z1&ox(u"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "constance",
    "debug_toolbar",
    "rest_framework",
    "timestamps",
    "mptt",
    "product",
    "shop.apps.ShopConfig",
    "promotion",
    "user",
    "order",
    "payment",
    "django_celery_beat",
    "django_celery_results",
    "rosetta",
]

AUTH_USER_MODEL = "user.CustomUser"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "config.jinja2.environment",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["static", "templates", BASE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis_db:6379",
    }
}

TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis_db:6379/5",
    }
}

# Django-constance settings
CONSTANCE_BACKEND = "constance.backends.redisd.CachingRedisBackend"
CONSTANCE_REDIS_CONNECTION = "redis://redis_db:6379"
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_REDIS_CACHE_TIMEOUT = 0

CONSTANCE_ADDITIONAL_FIELDS = {
    "choice_select": [
        "django.forms.fields.ChoiceField",
        {"widget": "django.forms.Select", "choices": (("No", "No"), ("Yes", "Yes"))},
    ],
}

CONSTANCE_CONFIG = {
    "COMMENTS_PER_PAGE": (3, "Count of comments per page"),
    "OBJECTS_PER_PAGE": (12, "Count of objects per page"),
    "ORDERS_PER_PAGE": (12, "Count of orders per page"),
    "PRODUCTS_PER_SHOP": (6, "Count of products per shop"),
    "COUNT_BANNERS": (3, "Count of banners per page"),

    "CLEAR_CACHE": ("No", "Clear all cache", "choice_select"),
    "CACHE_TIMEOUT": (60 * 60 * 24, "Cache timeout (default = 24 hours)"),
    "CACHE_KEY_PRODUCT_CATEGORY": (60 * 60 * 24, "Cache product category (default = 24 hours)"),
    "CACHE_KEY_BANNER": (60 * 10, "Banner cache timeout (default = 10 minutes)"),
    "CACHE_KEY_COMPARISON": (60 * 60 * 24 * 30, "Cache comparison (default = 1 month)"),
    "CACHE_KEY_CHECKOUT": (60 * 60, "Cache checkout (default = 1 hour)"),
    "CACHE_KEY_PAYMENT_ORDER": (60 * 20, "Cache timeout for payment (default = 20 minutes)"),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Cache options": (
        "CLEAR_CACHE",
        "CACHE_TIMEOUT",
        "CACHE_KEY_PRODUCT_CATEGORY",
        "CACHE_KEY_BANNER",
        "CACHE_KEY_COMPARISON",
        "CACHE_KEY_CHECKOUT",
        "CACHE_KEY_PAYMENT_ORDER",
    ),
    "Display Options": (
        "COMMENTS_PER_PAGE",
        "OBJECTS_PER_PAGE",
        "ORDERS_PER_PAGE",
        "PRODUCTS_PER_SHOP",
        "COUNT_BANNERS",
    ),
}

CACHE_KEY_PRODUCT_CATEGORY = "product_category"
CACHE_KEY_BANNER = "banner"
CACHE_KEY_COMPARISON = "comparison"
CACHE_KEY_CHECKOUT = "checkout"
CACHE_KEY_POPULAR_CATEGORY = "popular_category"
CACHE_KEY_PAYMENT_ORDER = "payment_order-{user_id}-{order_id}"

CACHE_TIMEOUT = {
    CACHE_KEY_PRODUCT_CATEGORY: CONSTANCE_CONFIG["CACHE_KEY_PRODUCT_CATEGORY"][0],
    CACHE_KEY_BANNER: CONSTANCE_CONFIG["CACHE_KEY_BANNER"][0],
    CACHE_KEY_COMPARISON: CONSTANCE_CONFIG["CACHE_KEY_COMPARISON"][0],
    CACHE_KEY_CHECKOUT: CONSTANCE_CONFIG["CACHE_KEY_CHECKOUT"][0],
    CACHE_KEY_POPULAR_CATEGORY: CONSTANCE_CONFIG["CACHE_KEY_CHECKOUT"][0],
    CACHE_KEY_PAYMENT_ORDER: CONSTANCE_CONFIG["CACHE_KEY_PAYMENT_ORDER"][0],
}

CART_SESSION_ID = "cart"
SESSION_COOKIE_AGE = CONSTANCE_CONFIG["CACHE_TIMEOUT"][0]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": "db",
        "PORT": 5432,
    }
}

CELERY_COUNTDOWN_ORDER = 30
CELERY_MAX_RETRIES_ORDER = 5

CELERY_BROKER_URL = "redis://redis_db/1"
CELERY_RESULT_BACKEND = "django-db"

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

# LANGUAGE_CODE = "en-us"
LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", _("Русский")),
    ("en", _("Английский")),
]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = ["static"]

STATIC_ROOT = os.path.join("", "staticfiles")

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

LOGIN_URL = "/login/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MPTT_ADMIN_LEVEL_INDENT = 20

# setting for Rosetta application that eases the translation process
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = "ru"
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = "Русский"
ROSETTA_SHOW_AT_ADMIN_PANEL = True
