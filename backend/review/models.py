from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint, CheckConstraint

from cocktail.models import Cocktail


class Review(models.Model):
    mark = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], null=True
    )
    text = models.TextField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    cocktail = models.ForeignKey(
        Cocktail, on_delete=models.CASCADE, related_name="user_reviews"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="cocktail_reviews"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "cocktail"],
                condition=models.Q(parent__isnull=True),
                name="unique_cocktail_review"
            ),
            CheckConstraint(
                condition=(
                    models.Q(parent__isnull=True, mark__isnull=False)
                    | models.Q(parent__isnull=False, mark__isnull=True)
                ),
                name="valid_mark_usage",
            ),
        ]
        indexes = [models.Index(fields=["cocktail", "parent"])]


class Like(models.Model):
    liked = models.BooleanField()
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="likes"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        unique_together = ["user", "review"]
        indexes = [models.Index(fields=["review", "liked"])]
