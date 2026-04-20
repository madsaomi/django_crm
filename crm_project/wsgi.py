"""
WSGI config for crm_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')

application = get_wsgi_application()

# Vercel Startup: Initialize ephemeral database from JSON if it's missing in /tmp
if os.environ.get('VERCEL'):
    import os
    from django.core.management import call_command
    from django.conf import settings
    
    db_path = settings.DATABASES['default']['NAME']
    if not os.path.exists(db_path):
        print("Initializing ephemeral database...")
        try:
            call_command('migrate', noinput=True)
            call_command('loaddata', 'initial_data.json')
            
            # Superuser check (from init_db.py)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        except Exception as e:
            print(f"Auto-initialization failed: {e}")
