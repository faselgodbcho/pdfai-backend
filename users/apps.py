from django.apps import AppConfig
from django.contrib.auth import get_user_model


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError

        try:
            User = get_user_model()
            username = "fasel"
            email = "faselgodbcho@gmail.com"
            password = "i_love_dogs_123"

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username, email=email, password=password)
                print(f"[INFO] Superuser '{username}' created.")
        except (OperationalError, ProgrammingError):
            # DB might not be ready during migration
            pass
