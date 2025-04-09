"""
Django settings for myapi project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
from datetime import timedelta
import environ

# SITE_URL = 'http://127.0.0.1:8000'  # 개발 환경시 활성화
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')

APPEND_SLASH = False

APPEND_SLASH = False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# env
env=environ.Env(DEBUG=(bool,False))
environ.Env.read_env(os.path.join(BASE_DIR,'.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=env('DEBUG')
# DEBUG=True
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

ALLOWED_HOSTS=['*'] #개발환경 시 활성화가 편함함

CORS_ORIGIN_ALLOW_ALL=True
CORS_ALLOW_CREDENTIALS=True

# Application definition
THIRD_PARTIES = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework.authtoken',
    'dj_rest_auth',
]
INSTALLED_APPS = [
    # 'django_extensions',
    'trade_hantu.apps.TradeHantuConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'doodook',
    'users',
    'trading.apps.TradingConfig',
    'stocks',
    'MBTI',
    'stock_search',
    'chatbot',   
    'guides',
    # 'corsheaders',
]+ THIRD_PARTIES

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', ## 이거 추가!! 위치 중요!!!
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', ## 이거 추가!!
]

ROOT_URLCONF = 'myapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
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

WSGI_APPLICATION = 'myapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
import json
# OPTIONS를 직접 파싱해서 딕셔너리로 처리
db_options = os.getenv('DB_OPTIONS', '{}')
if db_options:
    try:
        db_options = json.loads(db_options)
    except json.JSONDecodeError:
        db_options = {}

        
import pymysql
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': db_options,
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'doodook_db',
#         'USER': 'ham22',
#         'PASSWORD' : '',
#         'HOST' : 'svc.sel4.cloudtype.app',
#         'PORT' : '30898',
#         'OPTIONS':{
#             'init_command' : "SET sql_mode = 'STRICT_TRANS_TABLES'"
#         }
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'#0108 추가

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated",],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        #"rest_framework.authentication.SessionAuthentication",
    ],
}

JWT_AUTH = {
    "JWT_SECRET_KEY": SECRET_KEY, 
    "JWT_ALGORITHM": "HS256", # 암호화 알고리즘
    "JWT_ALLOW_REFRESH": True,
    "JWT_EXPIRATION_DELTA": timedelta(days=7), # 유효기간
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=28), # JWT 토큰 갱신 유효기간
}

#smtp
#이메일 인증
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER=env('EMAIL_HOST_USER')
#os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=env('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_MAIL = EMAIL_HOST_USER


# BASE_DIR = Path(__file__).resolve().parent.parent

HANTU_API_APP_KEY = env("HANTU_API_APP_KEY")
HANTU_API_APP_SECRET= env("HANTU_API_APP_SECRET")


# 추가: 한국투자증권 설정
# KIS_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'kis_devlp.yaml')