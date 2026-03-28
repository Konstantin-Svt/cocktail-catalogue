from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from cocktail.models import Cocktail


class EmailUserManager(UserManager):
    def _create_user_object(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, email, password, **extra_fields):
        user = self._create_user_object(email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, email, password, **extra_fields):
        user = self._create_user_object(email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    async def acreate_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    async def acreate_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(email, password, **extra_fields)


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        M = "male"
        F = "female"
        OTHER = "other"

    objects = EmailUserManager()
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    email_verified = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=60, choices=GenderChoices.choices, null=True, blank=True
    )
    country = models.CharField(max_length=50, null=True, blank=True)
    favourite_cocktails = models.ManyToManyField(
        Cocktail, blank=True, related_name="in_users_favourite"
    )

    def __str__(self):
        return self.email


class Rate(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="rates"
    )
    cocktail = models.ForeignKey(
        Cocktail, on_delete=models.CASCADE, related_name="rates"
    )
    mark = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ["user", "cocktail"]


class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="reviews")
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField(max_length=600)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "cocktail"]
