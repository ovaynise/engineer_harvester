from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    EntityViewSet,
    ConstructionsViewSet,
    ReminderViewSet,
    UserViewSet,
    ConstructionsWorksViewSet,
    ConstructionsCompanyViewSet,
    LocationViewSet,
    BrandTypeViewSet,
    BannedListViewSet,
    TelegramUserViewSet,
)

schema_view = get_schema_view(
   openapi.Info(
      title="XTRED_API",
      default_version='v1',
      description="Документация для проекта XTRED_site",
      contact=openapi.Contact(email="apply.powder.0p@icloud.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=( permissions.AllowAny, ),
)

router = DefaultRouter()
router.register('constructions', ConstructionsViewSet)
router.register('entity', EntityViewSet)
router.register('reminders', ReminderViewSet)
router.register('users', UserViewSet)
router.register('tg-users', TelegramUserViewSet)
router.register('banlist', BannedListViewSet)
router.register('constructions-works', ConstructionsWorksViewSet)
router.register('constructions-company', ConstructionsCompanyViewSet)
router.register('location', LocationViewSet)
router.register('brand-type', BrandTypeViewSet)


app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
