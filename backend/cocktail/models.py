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


class CocktailQuerySet(models.QuerySet):
    def with_levels(self):
        return self.annotate(
            alcohol_level=models.Case(
                *[
                    models.When(
                        alcohol_scale__lte=level.max_v,
                        alcohol_scale__gte=level.min_v,
                        then=models.Value(level.name),
                    )
                    for level in Cocktail.ALCOHOL_SCALE_MAP
                ],
                output_field=models.CharField(),
            ),
            sweetness_level=models.Case(
                *[
                    models.When(
                        sweetness_scale__lte=level.max_v,
                        sweetness_scale__gte=level.min_v,
                        then=models.Value(level.name),
                    )
                    for level in Cocktail.SWEETNESS_SCALE_MAP
                ],
                output_field=models.CharField(),
            ),
        )

    def with_ratings(self, with_avg: bool = False):
        res = self.annotate(
            one=models.Count(
                "user_reviews__mark", filter=models.Q(user_reviews__mark=1)
            ),
            two=models.Count(
                "user_reviews__mark", filter=models.Q(user_reviews__mark=2)
            ),
            three=models.Count(
                "user_reviews__mark", filter=models.Q(user_reviews__mark=3)
            ),
            four=models.Count(
                "user_reviews__mark", filter=models.Q(user_reviews__mark=4)
            ),
            five=models.Count(
                "user_reviews__mark", filter=models.Q(user_reviews__mark=5)
            ),
        )
        if with_avg:
            res = res.annotate(avg=models.Avg("user_reviews__mark"))
        return res


class Cocktail(models.Model):
    objects = CocktailQuerySet.as_manager()
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
    average_rating = models.FloatField(null=True, blank=True)
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

    def calculate_similar_cocktails(self):
        ingredient_ids = Ingredient.objects.filter(
            category__in=[
                Ingredient.Category.ALCOHOL,
                Ingredient.Category.MIXER,
            ],
            cocktails__id=self.pk,
        ).values_list("id", flat=True)
        similar_ids = tuple(
            Cocktail.objects.exclude(id=self.pk)
            .filter(ingredients__id__in=ingredient_ids)
            .distinct()
            .values_list("id", flat=True)
        )
        SimilarCocktails.objects.filter(
            (
                models.Q(to_cocktail_id=self.pk)
                & ~models.Q(from_cocktail_id__in=similar_ids)
            )
            | (
                models.Q(from_cocktail_id=self.pk)
                & ~models.Q(to_cocktail_id__in=similar_ids)
            )
        ).delete()
        relations = [
            SimilarCocktails(from_cocktail_id=self.pk, to_cocktail_id=cid)
            for cid in similar_ids
        ] + [
            SimilarCocktails(from_cocktail_id=cid, to_cocktail_id=self.pk)
            for cid in similar_ids
        ]
        if relations:
            SimilarCocktails.objects.bulk_create(
                relations, ignore_conflicts=True
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
        GLASS = "glass"

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cocktail.calculate_similar_cocktails()

    def delete(self, *args, **kwargs):
        cocktail = self.cocktail
        super().delete(*args, **kwargs)
        cocktail.calculate_similar_cocktails()


class Vibe(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower().strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
