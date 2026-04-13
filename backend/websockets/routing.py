from django.urls import path

from websockets.consumers import AIFiltersConsumer

websocket_urlpatterns = [
    path("ws/aifilters/", AIFiltersConsumer.as_asgi()),
]
