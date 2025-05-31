from django.urls import path
from .views import Home, search_contacts, get_messages, send_message, login_view, logout_view, register

urlpatterns = [
    path('', Home, name='home'),
    path("login/", login_view, name="user_login"),
    path("register/", register, name="user_register"),
    path("logout/", logout_view, name="user_logout"),
    path('search_contacts/', search_contacts, name='search_contacts'),
    path('get_messages/', get_messages, name='get_messages'),
    path('send_message/', send_message, name='send_message'),
]
