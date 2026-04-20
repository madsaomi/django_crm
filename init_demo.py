import os
import django
from django.core.management import call_command

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
    django.setup()

    print("--- Starting Demo Initialization ---")

    try:
        # 1. Run migrations
        print("Running migrations...")
        call_command('migrate', noinput=True)

        # 2. Load initial data from JSON
        print("Loading initial data from initial_data.json...")
        # Note: We use loaddata. If there's already data, it might conflict depending on PKs
        # but for a fresh SQLite it's perfect.
        call_command('loaddata', 'initial_data.json')

        # 3. Create superuser if it doesn't exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            print("Creating superuser 'admin'...")
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            print("Superuser created: admin / admin")
        else:
            print("Superuser 'admin' already exists.")

        print("--- Initialization Complete ---")
    except Exception as e:
        print(f"Error during initialization: {e}")
        # Note: We don't exit with error here to allow the server to try starting anyway
        # but in a real CI/CD you might want sys.exit(1)

if __name__ == '__main__':
    main()
