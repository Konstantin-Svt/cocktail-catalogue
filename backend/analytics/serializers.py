from rest_framework import serializers

from analytics.models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "event_name",
            "age_confirmed",
            "servings_number",
            "previous_filters",
        )
        required_fields = ("event_name",)

    def validate(self, data):
        if data["event_name"] not in (
            "age_confirmation",
            "servings_changed",
            "filters_reset",
        ):
            raise serializers.ValidationError(
                {"event_name": "Invalid event name"}
            )

        if data["event_name"] == "servings_changed" and not isinstance(
            data["servings_number"], int
        ):
            raise serializers.ValidationError(
                {"servings_number": "Invalid servings number"}
            )

        elif data["event_name"] == "age_confirmation" and not isinstance(
            data["age_confirmed"], bool
        ):
            raise serializers.ValidationError(
                {"age_confirmed": "Invalid age confirmation"}
            )

        elif data["event_name"] == "filters_reset" and not isinstance(
            data["previous_filters"], str
        ):
            raise serializers.ValidationError(
                {"filters_reset": "Invalid previous filters"}
            )

        return data
