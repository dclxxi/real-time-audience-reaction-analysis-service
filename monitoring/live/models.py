from django.db import models

from user.models import User


# Create your models here.

class CameraImage(models.Model):
    image = models.ImageField(upload_to="media")
    timestamp = models.DateTimeField(auto_now_add=True)


class Lecture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.TextField(max_length=50, null=False)
    datetime = models.DateTimeField(auto_now=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)

    class Meta:
        db_table = 'lecture'
