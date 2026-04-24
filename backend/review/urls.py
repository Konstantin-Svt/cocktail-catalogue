from django.urls import path, include
from rest_framework import routers

from review.views import (
    LoadMoreReviewsView,
    LoadNextRenderReviewsView,
    CreateReviewView,
    ReviewLikesViewSet,
)

likes_router = routers.DefaultRouter()
likes_router.register("", ReviewLikesViewSet)

urlpatterns = [
    path("load-more/", LoadMoreReviewsView.as_view(), name="load_more"),
    path("load-next/", LoadNextRenderReviewsView.as_view(), name="load_next"),
    path("add-review/", CreateReviewView.as_view(), name="add_review"),
    path("", include(likes_router.urls)),
]

app_name = "review"
