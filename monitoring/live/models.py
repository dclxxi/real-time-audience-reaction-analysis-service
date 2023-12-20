from django.db import models


# Create your models here.

class CameraImage(models.Model):
    image = models.ImageField(upload_to="이미지가 저장되는 디렉토리")
    timestamp = models.DateTimeField(auto_now_add=True)


class Lecture(models.Model):
    topic = models.CharField(max_length=50, null=False)
    datetime = models.DateTimeField(auto_now=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'lecture'


class Feedback(models.Model):
    time = models.TimeField()
    content = models.TextField()

    class Meta:
        db_table = 'feedback'
