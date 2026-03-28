import operator
from functools import reduce

from django.db.models import (
    Prefetch,
    Q,
    QuerySet,
    Case,
    When,
    Value,
    CharField,
)
from django.db.models.aggregates import Count
from django.http import QueryDict
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from catalogue_system.celery import (
    request_dict_converter,
    response_data_dict_converter,
)
from analytics.tasks import (
    cocktail_list_analytics_wrapper,
    cocktail_detail_analytics_wrapper,
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
            Q(cocktails__vibes__name__in=q_params.get("vibes").split(","))
        )
    if q_params.get("ingredients"):
        conditions.append(
            Q(
                cocktails__ingredients__name__in=q_params.get(
                    "ingredients"
                ).split(",")
            )
        )
    if q_params.get("alcohol_level"):
        alcohol_q = Q()
        for level in Cocktail.ALCOHOL_SCALE_MAP:
            if level.name in q_params.get("alcohol_level").split(","):
                alcohol_q |= Q(
                    cocktails__alcohol_scale__gte=level.min_v,
                    cocktails__alcohol_scale__lte=level.max_v,
                )
        conditions.append(alcohol_q)
    if q_params.get("sweetness_level"):
        sweet_q = Q()
        for level in Cocktail.SWEETNESS_SCALE_MAP:
            if level.name in q_params.get("sweetness_level").split(","):
                sweet_q |= Q(
                    cocktails__sweetness_scale__gte=level.min_v,
                    cocktails__sweetness_scale__lte=level.max_v,
                )
        conditions.append(sweet_q)
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
        qs = qs.filter(vibes__name__in=q_params.get("vibes").split(","))
    if q_params.get("ingredients"):
        qs = qs.filter(
            ingredients__name__in=q_params.get("ingredients").split(",")
        )
    if q_params.get("alcohol_level"):
        qs = qs.filter(
            alcohol_level__in=q_params.get("alcohol_level").split(",")
        )
    if q_params.get("sweetness_level"):
        qs = qs.filter(
            sweetness_level__in=q_params.get("sweetness_level").split(",")
        )
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
    queryset = Cocktail.objects.annotate(
        alcohol_level=Case(
            *[
                When(
                    alcohol_scale__lte=level.max_v,
                    alcohol_scale__gte=level.min_v,
                    then=Value(level.name),
                )
                for level in Cocktail.ALCOHOL_SCALE_MAP
            ],
            output_field=CharField(),
        ),
        sweetness_level=Case(
            *[
                When(
                    sweetness_scale__lte=level.max_v,
                    sweetness_scale__gte=level.min_v,
                    then=Value(level.name),
                )
                for level in Cocktail.SWEETNESS_SCALE_MAP
            ],
            output_field=CharField(),
        ),
    ).prefetch_related("vibes")
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
                .prefetch_related("ingredients")
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
                "similar_cocktails__vibes",
                "similar_cocktails__ingredients",
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
            f"{alcohol.name}_alcohol": Count(
                "id", filter=Q(alcohol_level=alcohol.name)
            )
            for alcohol in Cocktail.ALCOHOL_SCALE_MAP
        } | {
            f"{sweetness.name}_sweetness": Count(
                "id", filter=Q(sweetness_level=sweetness.name)
            )
            for sweetness in Cocktail.SWEETNESS_SCALE_MAP
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

        request_dict = request_dict_converter(request)
        response_dict = response_data_dict_converter(res.data)
        cocktail_list_analytics_wrapper.delay(request_dict, response_dict)

        res.data.update(summary)
        return res

    def retrieve(self, request, *args, **kwargs):
        res = super().retrieve(request, *args, **kwargs)
        request_dict = request_dict_converter(request)
        response_dict = response_data_dict_converter(res.data)
        cocktail_detail_analytics_wrapper.delay(request_dict, response_dict)
        return res


class VibeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vibe.objects.all()
    serializer_class = VibeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
