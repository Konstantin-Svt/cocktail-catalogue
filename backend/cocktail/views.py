import operator
from functools import reduce

from django.db.models import Prefetch, Q, QuerySet
from django.db.models.aggregates import Count
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cocktail.documentation import cocktail_filters_documentation
from cocktail.models import Cocktail, CocktailIngredients, Vibe, Ingredient
from cocktail.serializers import (
    CocktailListSerializer,
    CocktailDetailSerializer,
    VibeSerializer,
    IngredientSerializer,
)


def apply_annotate_filters(base_qs: QuerySet, q_params: dict) -> QuerySet:
    conditions = []
    if q_params.get("vibes"):
        conditions.append(
            Q(cocktails__vibes__name__in=q_params["vibes"].lower().split(","))
        )
    if q_params.get("ingredients"):
        conditions.append(
            Q(
                cocktails__ingredients__name__in=q_params["ingredients"]
                .lower()
                .split(",")
            )
        )
    if q_params.get("alcohol_lvl"):
        conditions.append(
            Q(
                cocktails__alcohol_level__in=q_params["alcohol_lvl"]
                .lower()
                .split(",")
            )
        )
    if q_params.get("sweetness_lvl"):
        conditions.append(
            Q(
                cocktails__sweetness_level__in=q_params["sweetness_lvl"]
                .lower()
                .split(",")
            )
        )
    filters = reduce(operator.and_, conditions, Q())
    return base_qs.annotate(cocktail_count=Count("cocktails", filter=filters))


def apply_queryset_filters(base_qs: QuerySet, q_params: dict) -> QuerySet:
    qs = base_qs
    if q_params.get("vibes"):
        qs = qs.filter(vibes__name__in=q_params["vibes"].lower().split(","))
    if q_params.get("ingredients"):
        qs = qs.filter(
            ingredients__name__in=q_params["ingredients"].lower().split(",")
        )
    if q_params.get("alcohol_lvl"):
        qs = qs.filter(
            alcohol_level__in=q_params["alcohol_lvl"].lower().split(",")
        )
    if q_params.get("sweetness_lvl"):
        qs = qs.filter(
            sweetness_level__in=q_params["sweetness_lvl"].lower().split(",")
        )
    return qs


class CocktailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cocktail.objects.prefetch_related("vibes")

    def get_serializer_class(self):
        if self.action == "list":
            return CocktailListSerializer
        if self.action == "retrieve":
            return CocktailDetailSerializer

    def get_queryset(self):
        qs = self.queryset

        if self.action == "list":
            return apply_queryset_filters(
                qs, self.request.query_params
            ).prefetch_related("ingredients")

        if self.action == "retrieve":
            return qs.prefetch_related(
                Prefetch(
                    "through_ingredients",
                    queryset=CocktailIngredients.objects.select_related(
                        "ingredient"
                    ),
                )
            )

    @cocktail_filters_documentation
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class VibeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vibe.objects.all()
    serializer_class = VibeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class SummaryAPIView(APIView):
    base_vibes = Vibe.objects.all()
    base_cocktails = Cocktail.objects.all()
    base_ingredients = Ingredient.objects.filter(
        category=Ingredient.Category.ALCOHOL
    )
    cocktails_enums = {
        f"{alcohol}_alcohol": Count("id", filter=Q(alcohol_level=alcohol))
        for alcohol in Cocktail.AlcoholLevel.values
    } | {
        f"{sweetness}_sweetness": Count(
            "id", filter=Q(sweetness_level=sweetness)
        )
        for sweetness in Cocktail.SweetnessLevel.values
    }

    @cocktail_filters_documentation
    def get(self, request):
        """Returns count of cocktails per each particular tag.
        Accepts same query params as cocktail list and
        dynamically recalculates result.
        """
        filtered_vibes = apply_annotate_filters(
            self.base_vibes, request.query_params
        )
        filtered_ingredients = apply_annotate_filters(
            self.base_ingredients, request.query_params
        )
        filtered_cocktails = apply_queryset_filters(
            self.base_cocktails, request.query_params
        ).aggregate(**self.cocktails_enums)
        vibe_count = {
            vibe.name: vibe.cocktail_count for vibe in filtered_vibes
        }
        ingredient_count = {
            ingredient.name: ingredient.cocktail_count
            for ingredient in filtered_ingredients
        }
        alcohol_count = {
            key.removesuffix("_alcohol"): value
            for key, value in filtered_cocktails.items()
            if "_alcohol" in key
        }
        sweetness_count = {
            key.removesuffix("_sweetness"): value
            for key, value in filtered_cocktails.items()
            if "_sweetness" in key
        }

        return Response(
            {
                "ingredient_count": ingredient_count,
                "alcohol_level_count": alcohol_count,
                "sweetness_level_count": sweetness_count,
                "vibe_count": vibe_count,
            },
            status=status.HTTP_200_OK,
        )
