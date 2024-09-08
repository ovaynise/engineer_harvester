from api.pagination import ConstructionPagination
from api.permissions import AuthorOrReadOnly
from constructions.models import (BrandType, Constructions,
                                  ConstructionsCompany, ConstructionsWorks,
                                  Entity, Location)
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from reminders.models import Reminder
from rest_framework import filters, permissions, viewsets
from users.models import BannedListModel, TelegramUserModel

from .serializers import (BannedListSerializer, BrandTypeSerializer,
                          ConstructionsCompanySerializer,
                          ConstructionsSerializer,
                          ConstructionsWorksSerializer, EntitySerializer,
                          LocationSerializer, MyUserSerializer,
                          ReminderSerializer, TelegramUserSerializer)

User = get_user_model()


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUserModel.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("tg_user_id", "id")


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("owner_reminder_id", "id")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BannedListViewSet(viewsets.ModelViewSet):
    queryset = BannedListModel.objects.all()
    serializer_class = BannedListSerializer
    permission_classes = (permissions.IsAdminUser,)


class ConstructionsWorksViewSet(viewsets.ModelViewSet):
    queryset = ConstructionsWorks.objects.all()
    serializer_class = ConstructionsWorksSerializer
    permission_classes = (AuthorOrReadOnly,)
    throttle_scope = "low_request"
    pagination_class = ConstructionPagination


class ConstructionsCompanyViewSet(viewsets.ModelViewSet):
    queryset = ConstructionsCompany.objects.all()
    serializer_class = ConstructionsCompanySerializer
    permission_classes = (AuthorOrReadOnly,)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (AuthorOrReadOnly,)


class BrandTypeViewSet(viewsets.ModelViewSet):
    queryset = BrandType.objects.all()
    serializer_class = BrandTypeSerializer
    permission_classes = (AuthorOrReadOnly,)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (permissions.IsAdminUser,)


class ConstructionsViewSet(viewsets.ModelViewSet):
    queryset = Constructions.objects.all()
    serializer_class = ConstructionsSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("brand", "date_acceptance")
    search_fields = ("title",)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (AuthorOrReadOnly,)
