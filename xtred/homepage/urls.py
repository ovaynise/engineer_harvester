from django.urls import path

from . import views
from auth_telegram import telegram_auth

app_name = "homepage"
urlpatterns = [
    path("", views.index, name="index"),
    path('telegram_auth/', telegram_auth, name='telegram_auth'),
]
