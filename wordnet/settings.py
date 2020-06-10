"""
Django settings for wordnet project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hz6y_a%ezm*qvv)lk-s4ugq6j+_$#y*b_)h1m$^jx5=&0gg-si'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wordnet.urls'

WSGI_APPLICATION = 'wordnet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/wordnet_static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "wordnet_static"),
)

LOGIN_URL = 'login'

#custom
DB_HOST = 'timemk.noip.me'
TRANSLATE_ONCE = True
POINTERS  =   { '!' : 'antonyms',
      
                '@' : 'hypernyms',
                '@i': 'instance_hypernyms',
      
                '~' : 'hyponyms',
                '~i': 'instance_hyponyms',
      
                '#m': 'member_holonyms',
                '#s': 'substance_holonyms',
                '#p': 'part_holonyms',
      
                '%m': 'member_meronyms',
                '%s': 'substance_meronyms',
                '%p': 'part_meronyms',
      
                '=' : 'attributes',
                '+' : 'drf',                      # Derivationally related form
      
                ';c': 'topic_domains',
                '-c': 'members_of_topic_domain',
      
                ';r': 'region_domains',
                '-r': 'members_of_region_domain',
      
                ';u': 'usage_domains',
                '-u': 'members_of_usage_domain',
      
                # verbs
                '*' : 'entailments',               # implies
                '>' : 'causes',            
                '^' : 'also_see',
                '$' : 'verb_groups',
                
                #adjectives
                '&' : 'similar',
                '<' : 'praticiple_of_verb',
                '\\': 'pertainym',

                #adverbs
                #'\\'  : 'Derived from adjective'

              }
