from django.urls import path

from . import views

app_name = 'live'

urlpatterns = [
    path("info/", views.info),
    path("cam/", views.cam),
    path("record/", views.record),
    path('media/', views.get_capture_file)
]
