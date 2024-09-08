# Generated by Django 4.2.14 on 2024-09-03 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("constructions", "0004_alter_constructionsworks_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brandtype",
            name="brand_photo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="photos/brand_photos/",
                verbose_name="Фото Брэнда",
            ),
        ),
    ]