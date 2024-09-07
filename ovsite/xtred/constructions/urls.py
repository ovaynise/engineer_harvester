from django.urls import path

from . import views
from core.views import add_comment

app_name = 'constructions'

urlpatterns = [
    path(
        '', views.СonstructionsListView.as_view(),
         name='constructions'
    ),
    path(
        'location/',
         views.LocationListView.as_view(),
         name='location'
    ),
    path(
        'create_location/',
        views.LocationCreateView.as_view(),
        name='create_location'
    ),
    path(
        'brand/',
         views.BrandTypeListView.as_view(),
         name='brandtype'
    ),
    path(
        'create_brand/',
        views.BrandTypeCreateView.as_view(),
        name='create_brand'
    ),
    path(
        'constructions_company/',
         views.ConstructionsCompanyListView.as_view(),
         name='constructions_company'
    ),
    path(
        'create/',
        views.ConstructionsCreateView.as_view(),
        name='create'
    ),
    path(
        'update/<int:pk>/',
        views.ConstructionsUpdateView.as_view(),
        name='update'
    ),
    path(
        'update_company/<int:pk>/',
        views.ConstructionsCompanyUpdateView.as_view(),
        name='update_company'
    ),
    path(
        'create_company/',
        views.ConstructionsCompanyCreateView.as_view(),
        name='create_company'
    ),
    path(
        'delete/<int:pk>/',
        views.ConstructionsDeleteView.as_view(),
        name='delete'
    ),
    path(
        'delete_company/<int:pk>/',
        views.ConstructionsCompanyDeleteView.as_view(),
        name='delete_company'
    ),
    path(
        'constructions_detail/<int:pk>/',
        views.ConstructionsDetailView.as_view(),
        name='constructions_detail'
    ),
    path(
        'constructions_company_detail/<int:pk>/',
        views.ConstructionsCompanyDetailView.as_view(),
        name='constructions_company_detail'
    ),
    path('<int:pk>/comment/', add_comment, name='add_comment'),
    path(
        'create_work/<int:pk>/',
        views.ConstructionsWorkCreateView.as_view(),
        name='create_work'
    ),

]
