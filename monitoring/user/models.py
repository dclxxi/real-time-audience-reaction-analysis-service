from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    profile_image = models.TextField()
    userid = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=24)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'userid'  # 고식별이 될 필드

    class Meta:
        db_table = "user"
