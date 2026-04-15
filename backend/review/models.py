from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint, CheckConstraint

from cocktail.models import Cocktail

User = get_user_model()


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
        User,
        on_delete=models.CASCADE,
        related_name="cocktail_reviews",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )

    class Meta:
        # constraints = [
        #     UniqueConstraint(
        #         fields=["user", "cocktail"],
        #         condition=models.Q(parent__isnull=True),
        #         name="unique_cocktail_review"
        #     ),
        #     CheckConstraint(
        #         condition=(
        #             models.Q(parent__isnull=True, mark__isnull=False)
        #             | models.Q(parent__isnull=False, mark__isnull=True)
        #         ),
        #         name="valid_mark_usage",
        #     ),
        # ]
        indexes = [
            models.Index(fields=["cocktail", "parent", "timestamp"]),
       ]

    def clean(self):
        if self._state.adding:
            if self.parent_id is None:
                if Review.objects.filter(
                    user_id=self.user_id,
                    cocktail_id=self.cocktail_id,
                    parent_id__isnull=True,
                ).exists():
                    raise ValidationError(
                        {
                            "cocktail_id": "Only one cocktail Review can be created."
                        }
                    )

            elif Review.objects.filter(
                id=self.parent_id, user_id=self.user_id
            ).exists():
                raise ValidationError(
                    {"parent_id": "Cannot reply to yourself."}
                )

    def recalculate_avg_rating(self):
        if self.parent_id is None and self.mark is not None:
            try:
                cocktail = (
                    Cocktail.objects.with_ratings(with_avg=True)
                    .get(id=self.cocktail_id)
                )
            except Cocktail.DoesNotExist:
                raise ValidationError({"cocktail_id": "Does not exist."})
            if cocktail.average_rating != cocktail.avg:
                cocktail.average_rating = round(cocktail.avg, 3)
                cocktail.save(update_fields=["average_rating"])

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.recalculate_avg_rating()


class Like(models.Model):
    liked = models.BooleanField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        unique_together = ["user", "review"]
        indexes = [models.Index(fields=["review", "liked"])]
