from django.db.models import Prefetch
from rest_framework import viewsets

from cocktail.models import Cocktail, CocktailIngredients, Tag, Ingredient
from cocktail.serializers import (
    CocktailListSerializer,
    CocktailDetailSerializer,
    TagSerializer,
    IngredientSerializer,
)


class CocktailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cocktail.objects.prefetch_related("tags")

    def get_serializer_class(self):
        if self.action == "list":
            return CocktailListSerializer
        if self.action == "retrieve":
            return CocktailDetailSerializer

    def get_queryset(self):
        qs = self.queryset
        if self.action == "list":
            return qs.prefetch_related("ingredients")
        if self.action == "retrieve":
            return qs.prefetch_related(
                Prefetch(
                    "through_ingredients",
                    queryset=CocktailIngredients.objects.select_related(
                        "ingredient"
                    ),
                )
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
