import os
import uuid
from collections import namedtuple

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify


def create_cocktail_image_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    path = f"{slugify(instance.name)}-{uuid.uuid4()}{ext}"
    return "cocktails/" + path


class Cocktail(models.Model):
    Level = namedtuple("Level", ["min_v", "max_v", "name"])
    ALCOHOL_SCALE_MAP = [
        Level(0, 0, "non-alcoholic"),
        Level(1, 3, "low"),
        Level(4, 7, "medium"),
        Level(8, 10, "strong"),
    ]
    SWEETNESS_SCALE_MAP = [
        Level(0, 3, "dry"),
        Level(4, 7, "medium"),
        Level(8, 10, "sweet"),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    alcohol_promille = models.PositiveIntegerField(default=0)
    alcohol_scale = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    sweetness_scale = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(10)]
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
        through_fields=("cocktail", "ingredient"),
        blank=True,
    )
    vibes = models.ManyToManyField(
        "Vibe", related_name="cocktails", blank=True
    )
    similar_cocktails = models.ManyToManyField(
        "self", blank=True, through="SimilarCocktails", symmetrical=True
    )

    def __str__(self):
        return self.name


class SimilarCocktails(models.Model):
    from_cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        related_name="similar_cocktails_from",
    )
    to_cocktail = models.ForeignKey(
        Cocktail, on_delete=models.CASCADE, related_name="similar_cocktails_to"
    )

    class Meta:
        unique_together = ("from_cocktail", "to_cocktail")
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_cocktail=models.F("to_cocktail")),
                name="prevent_self_cocktail_similarity",
            )
        ]


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

    class Meta:
        ordering = ("category",)

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
    alternative_ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="through_cocktails_alternative",
        null=True,
        blank=True,
    )
    cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        related_name="through_ingredients",
    )
    amount = models.PositiveIntegerField()
    optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ("cocktail", "ingredient")
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    ingredient=models.F("alternative_ingredient")
                ),
                name="prevent_ingredient_&_alt_similarity",
            )
        ]


class Vibe(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower().strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
