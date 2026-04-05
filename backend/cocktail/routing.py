from django.urls import path

from cocktail.consumers import AIFiltersConsumer

websocket_urlpatterns = [
    path("ws/aifilters/", AIFiltersConsumer.as_asgi()),
]
