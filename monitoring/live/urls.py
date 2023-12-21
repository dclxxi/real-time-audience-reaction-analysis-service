from django.urls import path

from . import views

app_name = 'live'

urlpatterns = [
    path("info/", views.info),
    path("cam/", views.cam),
    path("record/<int:id>/<int:term>/", views.record, name='record'),
    path('media/', views.get_capture_file),
    path('lectures/', views.lecture_list),
]
