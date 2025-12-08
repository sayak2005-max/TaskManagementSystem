import os
import sys

path = '/home/yourusername/TaskManagementSystem'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
