from rest_framework import serializers

from cocktail.models import Cocktail, Ingredient, CocktailIngredients, Vibe


class VibeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vibe
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
    alternative = serializers.StringRelatedField(
        source="alternative_ingredient"
    )

    class Meta:
        model = CocktailIngredients
        fields = (
            "id",
            "name",
            "category",
            "amount",
            "unit",
            "alternative",
            "optional",
        )
        read_only_fields = fields


class CocktailListSerializer(serializers.ModelSerializer):
    vibes = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = serializers.StringRelatedField(many=True, read_only=True)
    alcohol_level = serializers.CharField(
        read_only=True,
    )
    sweetness_level = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Cocktail
        fields = (
            "id",
            "name",
            "image",
            "average_price",
            "alcohol_level",
            "alcohol_promille",
            "sweetness_level",
            "preparation_time",
            "vibes",
            "ingredients",
        )
        read_only_fields = fields


class CocktailDetailSerializer(CocktailListSerializer):
    ingredients = IngredientForCocktailSerializer(
        many=True, read_only=True, source="through_ingredients"
    )
    similar_cocktails = CocktailListSerializer(many=True, read_only=True)
    vibes = VibeSerializer(many=True, read_only=True)

    class Meta(CocktailListSerializer.Meta):
        fields = CocktailListSerializer.Meta.fields + (
            "description",
            "preparation",
            "alcohol_scale",
            "sweetness_scale",
            "similar_cocktails",
        )
        read_only_fields = fields
