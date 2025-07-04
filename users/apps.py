import logging
from django.contrib.auth import get_user_model
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email='fasel@gmail.com',
                password='i_love_dogs',
                username='fasel'
            )

            logging.info("Superuser created automatically")
