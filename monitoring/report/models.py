from django.db import models

from live.models import Lecture
from django_mysql.models import ListCharField, ListTextField


# Create your models here.
class Reaction(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    time = models.IntegerField()
    concentration = models.IntegerField()
    negative = models.IntegerField()
    neutral = models.IntegerField()
    positive = models.IntegerField()

    class Meta:
        db_table = "reaction"


class Feedback(models.Model):
    reaction = models.OneToOneField(
        Reaction, on_delete=models.CASCADE, primary_key=True
    )
    content = models.TextField()
    strength = models.TextField()
    weakness = models.TextField()
    improvement = models.TextField()

    class Meta:
        db_table = "feedback"
