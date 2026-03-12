import os
import uuid

from django.db import models
from django.utils.text import slugify


def create_cocktail_image_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    path = f"{slugify(instance.name)}-{uuid.uuid4()}{ext}"
    return "cocktails/" + path


class Cocktail(models.Model):
    class AlcoholLevel(models.TextChoices):
        ZERO = "zero"
        LOW = "low"
        MEDIUM = "medium"
        STRONG = "strong"

    class SweetnessLevel(models.TextChoices):
        DRY = "dry"
        MEDIUM = "medium"
        SWEET = "sweet"

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    alcohol_level = models.CharField(
        choices=AlcoholLevel.choices, max_length=60
    )
    sweetness_level = models.CharField(
        choices=SweetnessLevel.choices, max_length=60
    )
    preparation = models.TextField(blank=True)
    preparation_time = models.PositiveIntegerField(default=5)
    image = models.ImageField(
        upload_to=create_cocktail_image_path, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(
        "Ingredient",
        related_name="cocktails",
        through="CocktailIngredients",
        blank=True,
    )
    vibes = models.ManyToManyField(
        "Vibe", related_name="cocktails", blank=True
    )
    similar_cocktails = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    class Category(models.TextChoices):
        ALCOHOL = "alcohol"
        MIXER = "mixer"
        GARNISH = "garnish"

    class Unit(models.TextChoices):
        ML = "ml"
        GRAM = "gram"
        PIECE = "piece"

    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(
        max_length=60,
        choices=Category.choices,
    )
    unit = models.CharField(
        max_length=60,
        choices=Unit.choices,
    )

    def save(self, *args, **kwargs):
        self.name = self.name.lower().strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CocktailIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="through_cocktails",
    )
    cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        related_name="through_ingredients",
    )
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ("cocktail", "ingredient")


class Vibe(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower().strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
