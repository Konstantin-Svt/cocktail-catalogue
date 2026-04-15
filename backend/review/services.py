from django.db.models import Window, F, Count, Q, OuterRef, Subquery
from django.db.models.functions import RowNumber

from review.models import Review, Like


def build_reviews_tree(
    cocktail_id: int,
    ordering: list,
    parent_id: int | None = None,
    skip_index: int | None = None,
    page_size: int = 10,
    current_depth: int = 0,
    max_depth: int = 2,
    max_children_len: int = 2,
    user_id: int | None = None,
) -> list:
    max_depth = min(9, max_depth) - current_depth
    if max_depth < 0:
        raise ValueError("current_depth can't be higher than max_depth")

    nodes = dict()
    base_qs = Review.objects.filter(cocktail_id=cocktail_id).annotate(
        positive_likes=Count("likes", filter=Q(likes__liked=True)),
        dislikes=Count("likes", filter=Q(likes__liked=False)),
    )
    if user_id is not None:
        user_liked = Like.objects.filter(
            user_id=user_id, review=OuterRef("pk")
        ).values("liked")[:1]
        base_qs = base_qs.annotate(user_liked=Subquery(user_liked))

    if skip_index is None:
        skip = 0
    else:
        skip = skip_index + 1

    limit = skip + page_size
    qs = (
        base_qs.filter(parent_id=parent_id)
        .order_by(*ordering)
        .select_related("user")
        .only(
            "id",
            "mark",
            "timestamp",
            "text",
            "cocktail_id",
            "parent_id",
            "user__id",
            "user__is_active",
            "user__first_name",
            "user__last_name",
        )[skip : limit + 1]
    )

    for i, root in enumerate(qs, start=skip):
        root.index = i
        root.depth = current_depth
        root.has_more = False
        root.hidden_children = False
        root.children = []
        nodes[root.pk] = root

    if len(qs) > page_size:
        nodes.popitem()
        nodes[next(reversed(nodes))].has_more = True

    prev_layer = list(nodes.keys())
    roots = list(nodes.values())

    for depth in range(max_depth + 1):
        is_last_layer = depth == max_depth

        if is_last_layer:
            curr_layer = base_qs.filter(parent_id__in=prev_layer).only(
                "id", "parent_id", "cocktail_id"
            )
            for node in curr_layer:
                parent = nodes.get(node.parent_id)
                if not parent:
                    continue
                parent.hidden_children = True
        else:
            ordering = [F("parent_id")] + ordering
            curr_layer = list(
                base_qs.filter(parent_id__in=prev_layer)
                .annotate(
                    rn=Window(
                        expression=RowNumber(),
                        partition_by=[F("parent_id")],
                        order_by=ordering,
                    )
                )
                .filter(rn__lte=max_children_len + 1)
                .select_related("user")
                .only(
                    "id",
                    "mark",
                    "timestamp",
                    "text",
                    "cocktail_id",
                    "parent_id",
                    "user__id",
                    "user__is_active",
                    "user__first_name",
                    "user__last_name",
                )
            )
            prev_layer = []
            if curr_layer:
                prev_parent = curr_layer[0].parent_id

            for i, node in enumerate(curr_layer):
                if (
                    node.rn > max_children_len
                    and node.parent_id == prev_parent
                    and i != 0
                ):
                    curr_layer[i - 1].has_more = True
                    continue
                parent = nodes.get(node.parent_id)
                if not parent:
                    continue
                node.index = node.rn - 1
                node.depth = parent.depth + 1
                if not hasattr(node, "has_more"):
                    node.has_more = False
                node.hidden_children = False
                node.children = []
                parent.children.append(node)
                nodes[node.pk] = node
                prev_layer.append(node.pk)
                if prev_parent != node.parent_id:
                    prev_parent = node.parent_id

    return roots


def flatten_reviews_tree(roots: list) -> list:
    result = []
    stack = list(reversed(roots))
    while stack:
        node = stack.pop()
        stack.extend(reversed(getattr(node, "children", [])))
        node.children = None
        result.append(node)

    return result
