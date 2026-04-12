from rest_framework import serializers

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
            "timestamp",
            "parent_id",
            "has_more",
            "hidden_children",
            "index",
            "depth",
            "children"
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
            "timestamp",
            "parent_id",
            "has_more",
            "hidden_children",
            "index",
            "depth",
        )
