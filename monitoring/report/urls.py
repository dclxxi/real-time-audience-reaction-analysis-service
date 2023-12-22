from django.urls import path

from . import views

app_name = 'report'

urlpatterns = [
    path("result/<int:id>/", views.result),
]
