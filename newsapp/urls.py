from django.urls import path
from .views import fetch_news, get_news, index, register_user, login_user  # Import auth views

urlpatterns = [
    path('', index, name='index'),
    path('fetch-news/', fetch_news, name='fetch-news'),
    path('get-news/', get_news, name='get-news'),

    # Authentication Routes
    path("signup/", register_user, name="register_user"),
    path("login/", login_user, name="login"),
]
