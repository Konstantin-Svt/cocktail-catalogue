from django.urls import path

from analytics.views import EventCreate

urlpatterns = [path("events/", EventCreate.as_view(), name="event-create"), ]

app_name = "analytics"
