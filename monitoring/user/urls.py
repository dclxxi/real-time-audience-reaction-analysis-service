from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path("signup/", views.signup_view),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
]
