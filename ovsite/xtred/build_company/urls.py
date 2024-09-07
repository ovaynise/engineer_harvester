from django.urls import path

from . import views

app_name = "build_company"
urlpatterns = [
    path("", views.build_company, name="build_company"),
]
