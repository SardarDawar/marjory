import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'x6cc!$soooiurvcv8m4dhj$3v3bju5jpuh*p&h)%65aldqldap'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost',"167.172.142.0",'127.0.0.1','inference.app.br','marjory.inference.app.br']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # imported apps
    'admin_reorder',
    'django_cleanup.apps.CleanupConfig',
    'crispy_forms',
    'colorfield',
    # site apps
    'common.apps.CommonConfig',
    'studies.apps.StudiesConfig',
    'scripts.apps.ScriptsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # custom middleware
    'common.middleware.AppMiddleware',
    ##################################
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # imported middleware
    'admin_reorder.middleware.ModelAdminReorder',
]

ADMIN_REORDER = (
    {'app': 'auth'},
    {'app': 'sites', 'label': 'Sites and Settings', 'models': (
        'sites.Site',
        'common.Setting',
        'common.Link',
    )},
    {'app': 'studies', 'models': (
        'studies.Study',
        'studies.Replica',
        'studies.Image',
    )},
    {'app': 'scripts', 'models': (
        'scripts.Script',
        'scripts.Step',
        'scripts.Component',
        'scripts.InterestedPerson',
    )},
)

ROOT_URLCONF = 'marjory.urls'
SITE_ID = 2

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join('templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # custom context processor
                'common.context_processors.site_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'marjory.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.mysql',
       'NAME': 'defaultdb',
       'USER': 'doadmin',
       'PASSWORD':'t04xkosfto9bvpjs',
       'HOST':'marjorydatabase-do-user-8358100-0.b.db.ondigitalocean.com',
       'PORT':'25060'

 }
}

# this uses sqlite (to switch to mysql, comment this out and use the above 'DATABASES' variable, and provide the required credentials)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR,'static')


SSTATICFILES_DIRS=[
    STATIC_ROOT,

    ]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# email host configuration (not used)
# EMAIL_BACKEND =         'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS =         True
# EMAIL_HOST =            'smtp.gmail.com'
# EMAIL_HOST_USER =       ''        # os.environ.get('MARJORY_EMAIL_HOST_USER'),
# EMAIL_HOST_PASSWORD =   ''        # os.environ.get('MARJORY_EMAIL_HOST_PASS'),
# EMAIL_PORT =            587

# django-crispy-forms configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'
