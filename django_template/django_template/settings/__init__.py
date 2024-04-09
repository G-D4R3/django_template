import os

ENV_SETTINGS_MODE = os.environ.get('ENV_SETTINGS_MODE')

if ENV_SETTINGS_MODE is None:
    ENV_MODE = 'local'
elif ENV_SETTINGS_MODE == 'prod':
    ENV_MODE = 'prod'
else:
    ENV_MODE = 'local'

if ENV_MODE == 'prod':
    from django_template.settings.prod import *
else:
    from django_template.settings.local import *
