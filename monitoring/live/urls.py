from django.urls import path

from . import views

app_name = 'live'

urlpatterns = [
    path("info/", views.info),
    path("cam/", views.cam),
    path("record/", views.record),
]
