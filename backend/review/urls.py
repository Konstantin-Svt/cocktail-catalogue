from django.urls import path

from review.views import LoadMoreReviewsView, LoadNextRenderReviewsView, CreateReviewView

urlpatterns = [
    path("load-more/", LoadMoreReviewsView.as_view(), name="load_more"),
    path("load-next/", LoadNextRenderReviewsView.as_view(), name="load_next"),
    path("add-review/", CreateReviewView.as_view(), name="add_review"),
]

app_name = "review"
