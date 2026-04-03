from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analytics.models import Event
from analytics.serializers import EventCreateSerializer
from analytics.services import create_event_from_frontend


class EventCreate(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateSerializer
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        Endpoint for all kinds of analytics events sent from the frontend.
        Does not return anything even if an event is registered successfully.
        """
        super().post(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)

    def head(self, request):
        return Response()

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        create_event_from_frontend(serializer, self.request)
