from django.contrib.auth import get_user_model

from rest_framework import serializers

from constructions.models import (Constructions,
                                  Entity,
                                  BrandType,
                                  Location,
                                  ConstructionsCompany,
                                  ConstructionsWorks)

from reminders.models import Reminder
from users.models import TelegramUserModel, BannedListModel

User = get_user_model()


class BannedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannedListModel
        fields = ('__all__')


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUserModel
        fields = ('__all__')


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')


class ConstructionsWorksSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionsWorks
        fields = (
            'id',
            'work',
            'date_start',
            'date_finish',
            'constructions',
            'constructions_company'
        )


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'city', 'country')


class BrandTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandType
        fields = ('id', 'title', 'brand_photo')


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = (
            'id',
            'reminder_nickname',
            'name_reminder',
            'text_reminder',
            'days_repeat',
            'status_reminder',
            'night_mode',
            'interval_repeat',
            'chats_id_active',
            'chats_names_active',
            'owner_reminder_id',
            'reminder_last_view_time',
            'next_reminder_time',
            'updated_at'
        )


class ConstructionsCompanySerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField(read_only=True)
    entity = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ConstructionsCompany
        fields = ('id', 'title', 'email', 'phone_number', 'location', 'entity')


class ConstructionsSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    location = serializers.StringRelatedField(read_only=True)
    brand = serializers.StringRelatedField(read_only=True)
    constructions_company = ConstructionsCompanySerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Constructions
        fields = (
            'id',
            'constructions_company',
            'author',
            'title',
            'description',
            'date_start',
            'date_finish',
            'date_acceptance',
            'address_object',
            'brand',
            'location',
            'latitude',
            'longitude',
        )


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ('id', 'title')
