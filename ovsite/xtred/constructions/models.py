from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Entity(BaseModel):
    title = models.CharField(
        max_length=128, verbose_name="Юр.лицо", unique=True
    )

    class Meta:
        verbose_name = "Юридическое лицо"

    def __str__(self):
        return self.title


class BrandType(BaseModel):
    title = models.CharField(
        max_length=128, verbose_name="Брэнд", default="Татнефть", unique=True
    )
    brand_photo = models.ImageField(
        upload_to="photos/brand_photos/",
        verbose_name="Фото Брэнда",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Брэнд АЗС"

    def __str__(self):
        return self.title


class Location(BaseModel):
    country = models.CharField(
        max_length=255,
        default="Российская Федерация",
        verbose_name="Страна",
    )
    city = models.CharField(
        max_length=255,
        default="не назначен",
        verbose_name="Город",
        unique=True,
    )

    class Meta:
        verbose_name = "Локация"

    def __str__(self):
        return self.city


class ConstructionsCompany(BaseModel):
    title = models.CharField(
        max_length=128, verbose_name="Название Организации", unique=True
    )
    email = models.EmailField(
        default="отсутствует",
        verbose_name="email почта",
        max_length=254,
        unique=True,
    )
    phone_number = models.CharField(
        default="отсутствует",
        verbose_name="Мобильный номер",
        max_length=20,
        unique=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="location_company",
        verbose_name="Основной регион подрядчика",
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="entity",
        verbose_name="Юр.лицо по договору",
        null=True,
        blank=True,
    )

    def completed_constructions(self):
        return Constructions.objects.filter(
            constructions_company=self,
            date_finish__isnull=False,
            date_acceptance__isnull=False,
        )

    def active_constructions(self):
        return Constructions.objects.filter(
            constructions_company=self,
            date_acceptance__isnull=True,
            date_finish__isnull=True,
            date_start__lt=timezone.now(),
        )

    def completed_brands(self):
        completed_constructions = Constructions.objects.filter(
            constructions_company=self,
            date_finish__isnull=False,
            date_acceptance__isnull=False,
        )
        unique_brands = completed_constructions.values("brand").distinct()
        return unique_brands.count()

    def unique_locations_count(self):
        constructions = Constructions.objects.filter(
            constructions_company=self
        )
        unique_cities = constructions.values("location__city").distinct()
        return unique_cities.count()

    def last_construction(self):
        completed_constructions = Constructions.objects.filter(
            constructions_company=self, date_acceptance__isnull=False
        ).order_by("-date_acceptance")

        return (
            (completed_constructions.first())
            if completed_constructions.exists()
            else None
        )

    class Meta:
        verbose_name = "Подрядчик"
        verbose_name_plural = "Подрядчики"

    def __str__(self):
        return self.title


class Constructions(BaseModel):
    title = models.CharField(max_length=128, verbose_name="Номер АЗС")
    description = models.CharField(
        max_length=128,
        default="Нет описания",
        verbose_name="Описание",
        blank=True,
        null=True,
    )
    date_start_graph = models.DateField(
        verbose_name="Дата начала строительства по графику",
        blank=True,
        null=True,
    )
    date_finish_graph = models.DateField(
        verbose_name="Дата окончания строительства по графику",
        blank=True,
        null=True,
    )
    date_start = models.DateField(
        verbose_name="Дата начала строительства", blank=True, null=True
    )
    date_finish = models.DateField(
        verbose_name="Дата окончания строительства", blank=True, null=True
    )
    date_acceptance = models.DateField(
        verbose_name="Дата приемки строительства", blank=True, null=True
    )
    address_object = models.CharField(
        max_length=255,
        default="не назначен",
        verbose_name="Адрес",
    )
    latitude = models.FloatField(
        verbose_name="Координаты Широта", blank=True, null=True
    )
    longitude = models.FloatField(
        verbose_name="Координаты Долгота", blank=True, null=True
    )

    constructions_company = models.ManyToManyField(
        ConstructionsCompany,
        related_name="constructions_company",
        verbose_name="Подрядчик",
        blank=True,
    )
    brand = models.ForeignKey(
        BrandType,
        on_delete=models.CASCADE,
        related_name="brand",
        verbose_name="Брэнд АЗС",
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="location",
        verbose_name="Город",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"

    def __str__(self):
        return self.title


class ConstructionsWorks(BaseModel):
    work = models.CharField(max_length=255, verbose_name="Вид работы")
    unit_of_measurement = models.CharField(
        max_length=50, verbose_name="Единица измерения", blank=True, null=True
    )

    quantity = models.FloatField(
        verbose_name="Количество", blank=True, null=True
    )

    constructions = models.ForeignKey(
        Constructions,
        on_delete=models.CASCADE,
        related_name="constructions_worksed",
    )
    constructions_company = models.ManyToManyField(
        ConstructionsCompany,
        related_name="constructions_worksed_company",
        blank=True,
    )
    date_start = models.DateField(
        verbose_name="Дата начала работ", blank=True, null=True
    )
    date_finish = models.DateField(
        verbose_name="Дата окончания работ", blank=True, null=True
    )

    class Meta:
        verbose_name = "Вид Работы"

    def __str__(self):
        return self.work


class Comment(BaseModel):
    text = models.TextField("Текст комментария")
    constructions = models.ForeignKey(
        Constructions,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        ordering = ("created_at",)
