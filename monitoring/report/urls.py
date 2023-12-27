from django.urls import path

from . import views

app_name = 'report'

urlpatterns = [
    path("list/", views.list),
    path("result/<int:id>/", views.result),
]
