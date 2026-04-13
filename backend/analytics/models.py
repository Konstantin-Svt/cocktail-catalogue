from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    anonymous_user_id = models.CharField(max_length=255)
    session_start = models.DateTimeField(default=timezone.now)
    session_end = models.DateTimeField(default=timezone.now)
    device_type = models.CharField(max_length=255, null=True, blank=True)
    browser = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Session of {self.anonymous_user_id}"


class Event(models.Model):
    class EventName(models.TextChoices):
        AGE_CONFIRMATION = "age_confirmation"
        PAGE_VIEW = "page_view"
        SEARCH_QUERY = "search_query"
        FILTER_APPLIED = "filter_applied"
        FILTERS_RESET = "filters_reset"
        CARD_VIEW = "cocktail_card_view"
        PAGE_OPEN = "cocktail_page_open"
        SERVINGS_CHANGED = "servings_changed"
        SIGNUP = "signup"
        LOGIN = "login"
        LOGOUT = "logout"
        RATING_ADDED = "rating_added"
        REVIEW_ADDED = "review_added"

    event_name = models.CharField(max_length=100, choices=EventName.choices)
    timestamp = models.DateTimeField(default=timezone.now)
    anonymous_user_id = models.CharField(max_length=255)
    session = models.ForeignKey(
        "Session", on_delete=models.SET_NULL, null=True, blank=True
    )
    page_name = models.CharField(max_length=255, null=True, blank=True)
    page_url = models.TextField(null=True, blank=True)
    cocktail = models.ForeignKey(
        "cocktail.Cocktail", on_delete=models.SET_NULL, null=True, blank=True
    )
    search_text = models.TextField(null=True, blank=True)
    filters_applied = models.BooleanField(null=True, blank=True)
    filter_type = models.CharField(max_length=100, null=True, blank=True)
    filter_value = models.CharField(max_length=255, null=True, blank=True)
    previous_filters = models.TextField(null=True, blank=True)
    results_count = models.PositiveIntegerField(null=True, blank=True)
    servings_number = models.PositiveIntegerField(null=True, blank=True)
    age_confirmed = models.BooleanField(null=True, blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    success = models.BooleanField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating_value = models.PositiveIntegerField(null=True, blank=True)
    review_length = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.event_name
