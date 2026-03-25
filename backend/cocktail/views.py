import operator
from functools import reduce

from django.db.models import Prefetch, Q, QuerySet
from django.db.models.aggregates import Count
from django.http import QueryDict
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from analytics.services import (
    create_page_view_event,
    create_card_view_events,
    create_filter_applied_events,
    create_cocktail_page_open_event,
)
from catalogue_system.pagination import StandardResultsSetPagination
from cocktail.documentation import cocktail_filters_documentation
from cocktail.models import (
    Cocktail,
    CocktailIngredients,
    Vibe,
    Ingredient,
)
from cocktail.serializers import (
    CocktailListSerializer,
    CocktailDetailSerializer,
    VibeSerializer,
    IngredientSerializer,
)


def apply_annotate_filters(base_qs: QuerySet, q_params: QueryDict) -> QuerySet:
    conditions = []
    if q_params.get("search"):
        conditions.append(
            (
                Q(cocktails__name__icontains=q_params["search"])
                | Q(cocktails__description__icontains=q_params["search"])
            )
        )
    if q_params.get("vibes"):
        conditions.append(
            Q(cocktails__vibes__name__in=q_params.getlist("vibes"))
        )
    if q_params.get("ingredients"):
        conditions.append(
            Q(cocktails__ingredients__name__in=q_params.getlist("ingredients"))
        )
    if q_params.get("alcohol_level"):
        conditions.append(
            Q(cocktails__alcohol_level__in=q_params.getlist("alcohol_level"))
        )
    if q_params.get("sweetness_level"):
        conditions.append(
            Q(
                cocktails__sweetness_level__in=q_params.getlist(
                    "sweetness_level"
                )
            )
        )
    if q_params.get("min_price"):
        if not q_params.get("min_price").isdigit():
            raise ValidationError("Min price must be an integer")
        conditions.append(
            Q(cocktails__average_price__gte=q_params["min_price"])
        )
    if q_params.get("max_price"):
        if not q_params.get("max_price").isdigit():
            raise ValidationError("Max price must be an integer")
        conditions.append(
            Q(cocktails__average_price__lte=q_params["max_price"])
        )

    filters = reduce(operator.and_, conditions, Q())
    return base_qs.annotate(
        cocktail_count=Count("cocktails", filter=filters, distinct=True)
    )


def apply_queryset_filters(base_qs: QuerySet, q_params: QueryDict) -> QuerySet:
    qs = base_qs
    if q_params.get("search"):
        qs = qs.filter(
            Q(name__icontains=q_params["search"])
            | Q(description__icontains=q_params["search"])
        )
    if q_params.get("vibes"):
        qs = qs.filter(vibes__name__in=q_params.getlist("vibes"))
    if q_params.get("ingredients"):
        qs = qs.filter(ingredients__name__in=q_params.getlist("ingredients"))
    if q_params.get("alcohol_level"):
        qs = qs.filter(alcohol_level__in=q_params.getlist("alcohol_level"))
    if q_params.get("sweetness_level"):
        qs = qs.filter(sweetness_level__in=q_params.getlist("sweetness_level"))
    if q_params.get("min_price"):
        if not q_params.get("min_price").isdigit():
            raise ValidationError("Min price must be an integer")
        qs = qs.filter(average_price__gte=q_params["min_price"])
    if q_params.get("max_price"):
        if not q_params.get("max_price").isdigit():
            raise ValidationError("Max price must be an integer")
        qs = qs.filter(average_price__lte=q_params["max_price"])
    return qs


class CocktailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cocktail.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return CocktailListSerializer
        if self.action == "retrieve":
            return CocktailDetailSerializer

    def get_queryset(self):
        qs = self.queryset
        if self.action == "list":
            return (
                apply_queryset_filters(qs, self.request.query_params)
                .prefetch_related(
                    Prefetch("vibes"),
                    Prefetch(
                        "through_ingredients",
                        queryset=CocktailIngredients.objects.select_related(
                            "ingredient"
                        ),
                    ),
                )
                .order_by("name")
                .distinct()
            )

        if self.action == "retrieve":
            return qs.prefetch_related(
                Prefetch(
                    "through_ingredients",
                    queryset=CocktailIngredients.objects.select_related(
                        "ingredient", "alternative_ingredient"
                    ),
                ),
                Prefetch(
                    "similar_cocktails",
                    queryset=Cocktail.objects.prefetch_related(
                        Prefetch("vibes", to_attr="prefetched_vibes"),
                        Prefetch(
                            "through_ingredients",
                            queryset=CocktailIngredients.objects.select_related(
                                "ingredient",
                            ),
                        ),
                    ),
                ),
            )

    @cocktail_filters_documentation
    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        general_count = res.data.pop("count", None)

        base_cocktails = self.get_queryset()
        base_vibes = Vibe.objects.all()
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

        filtered_cocktails = base_cocktails.aggregate(**cocktails_enums)
        filtered_vibes = apply_annotate_filters(
            base_vibes, request.query_params
        )
        filtered_ingredients = apply_annotate_filters(
            base_ingredients, request.query_params
        )

        vibes_count = {
            vibe.name: vibe.cocktail_count for vibe in filtered_vibes
        }
        ingredients_count = {
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
        summary = {
            "general_count": general_count,
            "ingredients_count": ingredients_count,
            "alcohol_level_count": alcohol_count,
            "sweetness_level_count": sweetness_count,
            "vibes_count": vibes_count,
        }

        analytic_session = create_page_view_event(request, "search")
        create_filter_applied_events(request, res, analytic_session)
        create_card_view_events(request, res, analytic_session)

        res.data.update(summary)
        return res

    def retrieve(self, request, *args, **kwargs):
        res = super().retrieve(request, *args, **kwargs)
        analytic_session = create_page_view_event(request, "cocktail_page")
        create_cocktail_page_open_event(request, res, analytic_session)
        return res


class VibeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vibe.objects.all()
    serializer_class = VibeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
