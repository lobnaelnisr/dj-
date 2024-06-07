
import os   
from pathlib import Path


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'django-insecure-lwd7pzt&(6*6^l8lmwoz6fdcrznsf959hzo%6*-4wuxltu4(0^'

#SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "False").lower() == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(" ")



# settings.py
import os

# Path to the model and scaler files
MODEL_PATH1 = os.path.join(BASE_DIR, 'svm_model (1).pkl')
MODEL_PATH2 = os.path.join(BASE_DIR, 'trained_model.pkl')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',

    'authapi.apps.AuthapiConfig',
    'rest_framework.authtoken',

    'rest_framework',

    'corsheaders',
    'fetchapi.apps.FetchapiConfig',

    'mlintegration.apps.MlIntegrationConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.AllowAny']}

CORS_ORIGIN_ALLOW_ALL = True  

CORS_ORIGIN_WHITELIST = [
    'http://localhost:5173',  
]

ROOT_URLCONF = 'project2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        
        'DIRS': [],
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

WSGI_APPLICATION = 'project2.wsgi.application'


#django.db.backends.mysql
#mysql.connector.django

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.mysql',

        'NAME': 'morphcast',
        'USER': 'lobna',
        'PASSWORD': '6101973',
        'HOST': 'insightlearn.me',
        'PORT': '3306',
    },
    'whole_db': {

        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'whole_proj',
        'USER': 'lobna',
        'PASSWORD': '6101973',
        'HOST': 'insightlearn.me',
        'PORT': '3306',
    },

}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True #

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')  #.
MEDIA_URL = "/media/"          #.

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#SMTP Conf:

EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST ='smtp.gmail.com'
EMAIL_PORT ='587'                                     #for TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER ='insightlearnmis@gmail.com'             #ur email
EMAIL_HOST_PASSWORD ='uets unyv heyo zmkj'         #ur password   
