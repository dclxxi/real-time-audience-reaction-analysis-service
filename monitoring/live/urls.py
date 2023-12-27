from django.urls import path

from . import views

app_name = 'live'

urlpatterns = [
    path("info/", views.info, name='info'),
    path("record/", views.info),
    path("record/<int:id>/<int:term>/", views.record, name='record'),
    path('media/', views.get_capture_file),
    path('video/', views.get_video_file),
]
