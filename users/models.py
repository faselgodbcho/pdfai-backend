from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    # required internally by django
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="settings")
    response_length = models.CharField(max_length=10, choices=[
        ("short", "Short"), ("medium", "Medium"), ("long", "Long")
    ], default="medium")
    tone = models.CharField(max_length=10, choices=[
        ("formal", "Formal"), ("casual", "Casual"), ("neutral", "Neutral")
    ], default="neutral")
    context_memory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s({self.user.email}) settings"
