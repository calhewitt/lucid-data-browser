# A sample WSGI file for setting up the data browser with Apache
import os
import sys
sys.path.append("/var/www/lucid-data-browser")
os.environ['DJANGO_SETTINGS_MODULE'] = 'data_browser.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
