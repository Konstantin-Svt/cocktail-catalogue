from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import serializers

from cocktail.models import Cocktail
from review.models import Review


class ReviewRecursiveSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    has_more = serializers.BooleanField()
    hidden_children = serializers.BooleanField()
    index = serializers.IntegerField()
    depth = serializers.IntegerField()

    class Meta:
        model = Review
        fields = (
            "id",
            "user_id",
            "cocktail_id",
            "text",
            "mark",
            "timestamp",
            "parent_id",
            "has_more",
            "hidden_children",
            "index",
            "depth",
            "children",
        )

    def get_children(self, obj):
        children = getattr(obj, "children", [])
        return ReviewRecursiveSerializer(children, many=True).data


class ReviewSerializer(serializers.ModelSerializer):
    has_more = serializers.BooleanField()
    hidden_children = serializers.BooleanField()
    index = serializers.IntegerField()
    depth = serializers.IntegerField()

    class Meta:
        model = Review
        fields = (
            "id",
            "user_id",
            "cocktail_id",
            "text",
            "mark",
            "timestamp",
            "parent_id",
            "has_more",
            "hidden_children",
            "index",
            "depth",
        )


class CreateReviewSerializer(serializers.ModelSerializer):
    mark = serializers.IntegerField(
        allow_null=True,
        required=False,
        min_value=1,
        max_value=5,
    )
    text = serializers.CharField(
        allow_null=True, allow_blank=True, min_length=5, max_length=500
    )
    cocktail_id = serializers.PrimaryKeyRelatedField(
        queryset=Cocktail.objects.all(),
        source="cocktail",
        required=False,
        allow_null=True,
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        source="parent",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "text",
            "mark",
            "cocktail_id",
            "parent_id",
            "user_id",
        )
        read_only_fields = (
            "id",
            "user_id",
        )

    def validate(self, data):
        if data["parent"] is None and data["cocktail"] is None:
            raise serializers.ValidationError(
                {"detail": "Specify either cocktail_id or parent_id."}
            )
        if data["parent"] is not None and data["cocktail"] is not None:
            raise serializers.ValidationError(
                {"detail": "Specify only one of cocktail_id or parent_id."}
            )
        if data["parent"] is not None and data["mark"]:
            raise serializers.ValidationError(
                {"mark": "Cannot set mark for reply."}
            )
        if data["cocktail"] is not None and data["mark"] is None:
            raise serializers.ValidationError(
                {"mark": "Review should have a mark."}
            )
        if data["parent"] is not None and not data["text"]:
            raise serializers.ValidationError(
                {"text": "Reply should have a text."}
            )
        return data

    def create(self, validated_data):
        try:
            obj = Review.objects.create(**validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.args[0])
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "Something went wrong."}
            )
        return obj
