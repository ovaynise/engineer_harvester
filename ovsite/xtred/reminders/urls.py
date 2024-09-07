from django.urls import path

from . import views


app_name = 'reminders'
urlpatterns = [

    path('', views.RemindersListView.as_view(), name='reminders'),
    path(
        'create/',
        views.RemindersCreateView.as_view(),
        name='create'
    ),
    path(
        'update/<int:pk>/',
        views.RemindersUpdateView.as_view(),
        name='update'
    ),
    path(
        'delete/<int:pk>/',
        views.RemindersDeleteView.as_view(),
        name='delete'
    )

]
