# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:395885@localhost/x.db'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, '../project_x/db_repository')
SQLALCHEMY_RECORD_QUERIES = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# mail server settings
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'p.vetokhin@gmail.com'
MAIL_PASSWORD = 'sarajyzuehdnfpep'

# administrator list
ADMINS = ['p.vetokhin@gmail.com']

# pagination
POSTS_PER_PAGE = 3

# available languages
LANGUAGES = {
    'en': 'English',
    'ru': 'Русский'
}

# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = 'pavetok'
MS_TRANSLATOR_CLIENT_SECRET = 'E7KytAqOyIS43reIBaobR9vXTj0GEDOcWPN5tj8lqAE'

# celery
BROKER_URL = 'sqla+postgresql://postgres:395885@localhost/celery.db'
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = 'sqla+postgresql://postgres:395885@localhost/results.db'

CELERY_IMPORTS = ("app.tasks", )

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
