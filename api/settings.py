import os
from pathlib import Path
from urllib.parse import quote_plus

# --- load .env ---
BASE_DIR = Path(__file__).resolve().parent.parent  # project root (where .env normally lives)
# prefer .env in BASE_DIR, fallback to find_dotenv()
from dotenv import load_dotenv, find_dotenv

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv(find_dotenv())

# small helper to accept multiple possible env-names (lets us support MONGO_* or MONGO_DB_* variants)
def getenv(*names, default=None):
    for n in names:
        v = os.environ.get(n)
        if v is not None and v != "":
            return v
    return default

# --- basic settings ---
SECRET_KEY = getenv("DJANGO_SECRET", default="dev-secret")
DEBUG = str(getenv("DEBUG", default="True")).lower() in ("1", "true", "yes")
# allow comma-separated list, trim whitespace and ignore empty entries
ALLOWED_HOSTS = [h.strip() for h in getenv("ALLOWED_HOSTS", default="*").split(",") if h.strip()]

# Mongo settings — accept either MONGO_* or MONGO_DB_* names
MONGO_HOST = getenv("MONGO_HOST", "MONGO_DB_HOST", default="localhost")
MONGO_PORT = getenv("MONGO_PORT", "MONGO_DB_PORT", default="27017")
MONGO_USER = getenv("MONGO_USER", "MONGO_DB_USERNAME", default="")
MONGO_PASS = getenv("MONGO_PASS", "MONGO_DB_PASSWORD", default="")
MONGO_DB_NAME = getenv("MONGO_DB_NAME", "MONGO_DB_NAME", default="zibal")
MONGO_AUTH_SOURCE = getenv("MONGO_AUTH_SOURCE", "MONGO_AUTH_SOURCE", default="admin")

# Build URI safely depending on whether username/password exist
if MONGO_USER and MONGO_PASS:
    MONGO_USER = quote_plus(MONGO_USER)
    MONGO_PASS = quote_plus(MONGO_PASS)
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource={MONGO_AUTH_SOURCE}"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}"

# ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'rest_framework',
    'reports'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}