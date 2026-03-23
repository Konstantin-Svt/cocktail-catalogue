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
    vibes = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

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

    def get_vibes(self, obj):
        return [str(vibe) for vibe in getattr(obj, "prefetched_vibes", [])]

    def get_ingredients(self, obj):
        return [
            str(through_obj.ingredient)
            for through_obj in obj.through_ingredients.all()
        ]


class CocktailDetailSerializer(CocktailListSerializer):
    ingredients = IngredientForCocktailSerializer(
        many=True, read_only=True, source="through_ingredients"
    )
    similar_cocktails = CocktailListSerializer(many=True, read_only=True)

    class Meta(CocktailListSerializer.Meta):
        fields = CocktailListSerializer.Meta.fields + (
            "description",
            "preparation",
            "similar_cocktails",
        )
        read_only_fields = fields
