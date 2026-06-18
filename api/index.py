import os
import sys

# Add backend directory to path so Django settings can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "log_filler_backend.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
