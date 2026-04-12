from django.urls import path

from review.views import LoadMoreReviewsView, LoadNextRenderReviewsView

urlpatterns = [
    path("load-more/", LoadMoreReviewsView.as_view(), name="load_more"),
    path("load-next/", LoadNextRenderReviewsView.as_view(), name="load_next"),
]

app_name = "review"
