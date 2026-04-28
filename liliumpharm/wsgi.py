import os
import sys
print(sys.path)

sys.path.append('/var/www/server')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')

application = get_wsgi_application()