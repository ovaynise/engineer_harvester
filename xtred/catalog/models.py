from django.db import models


class Catalog(models.Model):
    title = models.CharField(
        max_length=128, verbose_name="Каталог поставщиков"
    )

    class Meta:
        verbose_name = "Каталог"
        verbose_name_plural = "Каталоги"

    def __str__(self):
        return self.title
