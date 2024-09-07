from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    path(
        "profile/<slug:username>/",
        views.ProfileDetailView.as_view(),
        name="profile",
    ),
    path("update/", views.ProfileUpdateView.as_view(), name="edit_profile"),
    path("users/", views.UsersListView.as_view(), name="users"),
]
