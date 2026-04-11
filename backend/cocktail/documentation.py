from drf_spectacular.utils import OpenApiParameter, extend_schema

from catalogue_system.pagination import StandardResultsSetPagination

cocktail_filters_documentation = extend_schema(
    parameters=[
        OpenApiParameter(
            name="page", type=int, description="Page number for pagination."
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description=f"Page size for pagination. To adjust a "
            f"number of items shown per one page. "
            f"Max is {StandardResultsSetPagination.max_page_size}.",
        ),
        OpenApiParameter(
            name="search",
            type=str,
            description="Filters by searching given text in "
            "cocktails name or description (case insensitive).",
        ),
        OpenApiParameter(
            name="vibes",
            type=str,
            many=True,
            description="Accepts one or many vibes names "
            "separated by commas to filter cocktails "
            "with corresponding vibes. If more "
            "than one is given they are "
            "treated as OR clauses.",
        ),
        OpenApiParameter(
            name="ingredients",
            type=str,
            many=True,
            description="Accepts one or many ALCOHOLic ingredients "
            "names separated by commas to filter cocktails "
            "which ingredients contain corresponding alcohol name."
            " If more than one is given they are "
            "treated as OR clauses.",
        ),
        OpenApiParameter(
            name="alcohol_level",
            type=str,
            many=True,
            description="Accepts one or many alcohol levels "
            "separated by commas to filter cocktails "
            "with corresponding alcohol levels. "
            "If more than one is given they are "
            "treated as OR clauses.",
        ),
        OpenApiParameter(
            name="sweetness_level",
            type=str,
            many=True,
            description="Accepts one or many sweetness levels "
            "separated by commas to filter cocktails "
            "with corresponding sweetness levels. "
            "If more than one is given they are "
            "treated as OR clauses.",
        ),
        OpenApiParameter(
            name="min_price",
            type=int,
            description="Accepts minimum price integer to filter "
            "cocktails with higher or equal average price.",
        ),
        OpenApiParameter(
            name="max_price",
            type=int,
            description="Accepts maximum price integer to filter "
            "cocktails with lower or equal average price.",
        ),
    ]
)

cocktail_reviews_documentation = extend_schema(
    parameters=[
        OpenApiParameter(
            name="reviews_mode",
            type=str,
            description="cocktail reviews API appearance mode."
            "Possible values are 'flat' or 'tree'. Default is 'flat'."
            " In tree mode reviews have nested list field 'children'.",
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description=f"Number of reviews shown for level depth 0"
            " (or level 1 for NEXT RENDER). If not given default is 10",
        ),
        OpenApiParameter(
            name="max_depth",
            type=int,
            description="Maximum amount of replies depth level per one render"
            " (starting with 0 - no replies are shown)"
            "If not given default is 2, max is 9",
        ),
        OpenApiParameter(
            name="max_children_len",
            type=int,
            description="Maximum amount of nested replies "
            "list for all depth levels except for 0 "
            "(or 1 for NEXT RENDER) per one child. If not given default is 2",
        ),
    ]
)
