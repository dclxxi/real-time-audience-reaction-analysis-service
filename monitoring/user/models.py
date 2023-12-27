from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, userid):
        return self.get(userid=userid)


class User(AbstractBaseUser):
    profile_image = models.TextField(null=True)
    userid = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=24)
    email = models.EmailField(unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'userid'  # 고식별이 될 필드

    class Meta:
        db_table = "user"

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True
