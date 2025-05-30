from django.urls import path
from .views import hello
from .user import login_view, logout_view, register

urlpatterns = [
    path('', hello, name='user'),
    path("login/", login_view, name="user_login"),
    path("register/", register, name="user_register"),
    path("logout/", logout_view, name="user_logout"),
]
