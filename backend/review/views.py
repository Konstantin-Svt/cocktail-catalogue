from django.db.models import Case, When, Value, IntegerField
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cocktail.documentation import cocktail_reviews_documentation
from review.models import Review
from review.serializers import (
    ReviewRecursiveSerializer,
    ReviewSerializer,
    CreateReviewSerializer,
)
from review.services import build_reviews_tree, flatten_reviews_tree
from user.authentication import SafeJWTAuthentication


class LoadMoreReviewsView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (SafeJWTAuthentication,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                description="id of review that 'has_more'",
                required=True,
            ),
            OpenApiParameter(
                name="index",
                type=int,
                description="index of review that 'has_more'",
                required=True,
            ),
            OpenApiParameter(
                name="depth",
                type=int,
                description="depth of review that 'has_more'",
                required=True,
            ),
        ]
    )
    @cocktail_reviews_documentation
    def get(self, request, *args, **kwargs):
        reviews_mode = request.query_params.get("reviews_mode", "flat")
        if reviews_mode not in ("flat", "tree"):
            raise ValidationError("Invalid reviews_mode parameter.")

        int_params = {
            "id": request.query_params.get("id"),
            "index": request.query_params.get("index"),
            "depth": request.query_params.get("depth"),
            "page_size": request.query_params.get("page_size", 10),
            "max_depth": request.query_params.get("max_depth", 2),
            "max_children_len": request.query_params.get(
                "max_children_len", 2
            ),
        }
        for key, value in int_params.items():
            try:
                int_params[key] = int(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    {key: "Invalid parameter. Must be an integer."}
                )

        sort_by = request.query_params.get("sort_by", "timestamp")
        user_id = request.user.id if request.user.is_authenticated else None
        if user_id is not None:
            user_sort = Case(
                When(user_id=user_id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
            ordering = [user_sort, sort_by]
        else:
            ordering = [sort_by]

        upper_node = get_object_or_404(Review, id=int_params["id"])
        try:
            tree = build_reviews_tree(
                upper_node.cocktail_id,
                ordering,
                upper_node.parent_id,
                page_size=int_params["page_size"],
                max_depth=int_params["max_depth"],
                max_children_len=int_params["max_children_len"],
                user_id=user_id,
            )
        except ValueError as e:
            raise ValidationError(e)

        if reviews_mode == "tree":
            reviews_data = ReviewRecursiveSerializer(tree, many=True).data
        else:
            reviews = flatten_reviews_tree(tree)
            reviews_data = ReviewSerializer(reviews, many=True).data
        return Response(reviews_data)


class LoadNextRenderReviewsView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (SafeJWTAuthentication,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                description="id of review that has 'hidden_children'"
                " for next render",
                required=True,
            ),
        ]
    )
    @cocktail_reviews_documentation
    def get(self, request, *args, **kwargs):
        reviews_mode = request.query_params.get("reviews_mode", "flat")
        if reviews_mode not in ("flat", "tree"):
            raise ValidationError("Invalid reviews_mode parameter.")

        int_params = {
            "id": request.query_params.get("id"),
            "page_size": request.query_params.get("page_size", 10),
            "max_depth": request.query_params.get("max_depth", 2),
            "max_children_len": request.query_params.get(
                "max_children_len", 2
            ),
        }
        for key, value in int_params.items():
            try:
                int_params[key] = int(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    {key: "Invalid parameter. Must be an integer."}
                )

        sort_by = request.query_params.get("sort_by", "timestamp")
        user_id = request.user.id if request.user.is_authenticated else None
        if user_id is not None:
            user_sort = Case(
                When(user_id=user_id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
            ordering = [user_sort, sort_by]
        else:
            ordering = [sort_by]

        upper_node = get_object_or_404(Review, id=int_params["id"])
        try:
            tree = build_reviews_tree(
                upper_node.cocktail_id,
                ordering,
                upper_node.parent_id,
                page_size=int_params["page_size"],
                max_depth=int_params["max_depth"],
                max_children_len=int_params["max_children_len"],
                user_id=user_id,
            )
        except ValueError as e:
            raise ValidationError(e)

        if reviews_mode == "tree":
            reviews_data = ReviewRecursiveSerializer(tree, many=True).data
        else:
            reviews = flatten_reviews_tree(tree)
            reviews_data = ReviewSerializer(reviews, many=True).data
        return Response(reviews_data)


class CreateReviewView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateReviewSerializer
    queryset = Review.objects

    def post(self, request, *args, **kwargs):
        """
        Must be authenticated.
        Review must contain cocktail_id and mark, and can contain text.
        Reply must contain parent_id and text.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = {"user_id": request.user.id}

        if serializer.validated_data["parent"] is not None:
            params["cocktail_id"] = serializer.validated_data[
                "parent"
            ].cocktail_id

        serializer.save(**params)
        return Response(serializer.data)
