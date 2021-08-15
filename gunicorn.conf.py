import os
import multiprocessing


from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = settings.GUNICORN_ACCESS_LOG
errorlog = settings.GUNICORN_ERROR_LOG
