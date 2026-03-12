from drf_spectacular.utils import OpenApiParameter, extend_schema

cocktail_filters_documentation = extend_schema(
    parameters=[
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
            "names separated by commas to filter cocktails, "
            "which ingredients contain corresponding alcohol name."
            " If more than one is given they are "
            "treated as OR clauses.",
        ),
        OpenApiParameter(
            name="alcohol_lvl",
            type=str,
            many=True,
            description="Accepts one or many alcohol levels "
            "separated by commas to filter cocktails "
            "with corresponding alcohol levels. "
            "If more than one is given they are "
            "treated as OR clauses.",
        ),
        OpenApiParameter(
            name="sweetness_lvl",
            type=str,
            many=True,
            description="Accepts one or many sweetness levels "
            "separated by commas to filter cocktails "
            "with corresponding sweetness levels. "
            "If more than one is given they are "
            "treated as OR clauses.",
        ),
    ]
)
