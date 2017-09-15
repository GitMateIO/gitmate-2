"""
Django settings for the GitMate project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from ast import literal_eval
import os
import logging
import raven

from gitmate.utils import snake_case_to_camel_case


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            ('s#x)wcdigpbgi=7nxrbqbd&$yri@2k9bs%v@'
                             '*szo#&)c=qp+3-'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = literal_eval(os.environ.get('DJANGO_DEBUG', 'False'))
if DEBUG and not literal_eval(os.environ.get('FORCE_CELERY',
                                             'False')):  # pragma: nocover
    # let celery invoke all tasks locally
    CELERY_ALWAYS_EAGER = True
    # make celery raise exceptions when something fails
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

HOOK_DOMAIN = os.environ.get('HOOK_DOMAIN', 'localhost:8000')

# django>=1.11 requires tests to use allowed hosts
ALLOWED_HOSTS = ['testing.com', 'localhost', '127.0.0.1', 'localhost:4200',
                 'coala.io', HOOK_DOMAIN]
ALLOWED_HOSTS += os.environ.get('DJANGO_ALLOWED_HOSTS', '').split()
CORS_ORIGIN_WHITELIST = ALLOWED_HOSTS
CORS_ALLOW_CREDENTIALS = True

REQUISITE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'raven.contrib.django.raven_compat',
    'gitmate_config',
    'gitmate_logger',
    'rest_framework',
    'rest_framework_docs',
    'corsheaders',
    'coala_online',
    'coafile_bot'
]

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN'),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

GITMATE_PLUGINS = [
    'code_analysis',
    'welcome_commenter',
    'auto_label_pending_or_wip',
    'pr_size_labeller',
    'issue_labeller',
    'issue_assigner',
    'bug_spotter',
    'ack',
    'issue_pr_sync',
    'approver',
    'issue_stale_reminder',
    'pr_stale_reminder',
    'rebaser',
]

GITMATE_PLUGINS += [
    plugin
    for plugin in os.environ.get('EE_PLUGINS', '').split(' ')
    if plugin
]

# Application definition
INSTALLED_APPS = (REQUISITE_APPS +
                  ['plugins.gitmate_{}.apps.{}Config'.format(
                      name, snake_case_to_camel_case('gitmate_'+name))
                   for name in GITMATE_PLUGINS])

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    )
}

SOCIAL_AUTH_URL_NAMESPACE = 'auth'

# python-social-auth settings
SOCIAL_AUTH_LOGIN_REDIRECT_URL = os.environ.get(
    'SOCIAL_AUTH_REDIRECT', 'http://localhost:4200') + '/repositories'
SOCIAL_AUTH_LOGOUT_REDIRECT_URL = os.environ.get(
    'SOCIAL_AUTH_REDIRECT', 'http://localhost:4200')
SOCIAL_AUTH_LOGIN_URL = '/login'

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social.pipeline.user.user_details',
)

# Put gitmate's corresponding OAuth details here.
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
SOCIAL_AUTH_GITHUB_KEY = os.environ.get('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_SCOPE = [
    'admin:repo_hook',
    'repo',
]

SOCIAL_AUTH_GITLAB_KEY = os.environ.get(
    'SOCIAL_AUTH_GITLAB_KEY')
SOCIAL_AUTH_GITLAB_SECRET = os.environ.get('SOCIAL_AUTH_GITLAB_SECRET')
# This needs to be specified as is including full domain name and protocol.
# Be extra careful and use the same URL used while registering the application
# on GitLab. ex. example.com/auth/complete/gitlab/
SOCIAL_AUTH_GITLAB_REDIRECT_URL = os.environ.get(
    'SOCIAL_AUTH_GITLAB_REDIRECT_URL')
SOCIAL_AUTH_GITLAB_SCOPE = ['api']
SOCIAL_AUTH_GITLAB_API_URL = os.environ.get('GL_INSTANCE_URL',
                                            'https://gitlab.com')
if not SOCIAL_AUTH_GITLAB_API_URL.startswith('http'):  # pragma: no cover
    SOCIAL_AUTH_GITLAB_API_URL = 'https://' + SOCIAL_AUTH_GITLAB_API_URL
    logging.warning('Include the protocol in GL_INSTANCE_URL! Omitting it has '
                    'been deprecated.')

SOCIAL_AUTH_BITBUCKET_KEY = os.environ.get('SOCIAL_AUTH_BITBUCKET_KEY')
SOCIAL_AUTH_BITBUCKET_SECRET = os.environ.get('SOCIAL_AUTH_BITBUCKET_SECRET')

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.gitlab.GitLabOAuth2',
    'social_core.backends.bitbucket.BitbucketOAuth',
    'django.contrib.auth.backends.ModelBackend'
)

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gitmate.disable_csrf.DisableCSRF',
]

ROOT_URLCONF = 'gitmate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'gitmate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_ADDRESS', ''),
        'PORT': os.environ.get('DB_PORT', '')
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'console': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },

    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
            },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': RAVEN_CONFIG['dsn'],
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT',
                             os.path.join(BASE_DIR, 'static'))
STATIC_URL = '/static/'
STATICFILES_DIRS = ()


# CELERY CONFIG
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['json', 'pickle', 'yaml']

# RABBITMQ server base URL
BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                            'amqp://admin:password@rabbit/')

# This is required for coala_online
# Otherwise it throws NotImplementedError
CELERY_RESULT_BACKEND = 'amqp'

# coafile Bot Tokens
BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
BOT_USER = os.environ.get('BOT_USER', None)

# gitmate-2 repository details
ISSUE_REPORT_URL = os.environ.get('ISSUE_REPORT_URL',
                                  'https://gitlab.com/gitmate/open-source/'
                                  'gitmate-2/issues/new?issue_template=Bug&'
                                  'issue[title]={title}&'
                                  'issue[description]={description}')
