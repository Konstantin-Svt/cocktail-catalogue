from rest_framework import serializers

from cocktail.models import Cocktail, Ingredient, CocktailIngredients, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "category", "unit")
        read_only_fields = fields


class IngredientForCocktailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    category = serializers.CharField(source="ingredient.category")
    unit = serializers.CharField(source="ingredient.unit")

    class Meta:
        model = CocktailIngredients
        fields = ("id", "name", "category", "amount", "unit")
        read_only_fields = fields


class CocktailListSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Cocktail
        fields = (
            "id",
            "name",
            "image",
            "average_price",
            "alcohol_level",
            "sweetness_level",
            "tags",
            "ingredients",
        )
        read_only_fields = fields


class CocktailDetailSerializer(CocktailListSerializer):
    ingredients = IngredientForCocktailSerializer(
        many=True, read_only=True, source="through_ingredients"
    )
    tags = TagSerializer(many=True, read_only=True)

    class Meta(CocktailListSerializer.Meta):
        fields = CocktailListSerializer.Meta.fields + (
            "description",
            "preparation",
            "similar_cocktails",
        )
