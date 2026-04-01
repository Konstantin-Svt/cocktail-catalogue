from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import (
    ManageUserView,
    CreateUserView,
    TokenObtainCookiePairView,
    TokenRefreshCookieView,
    EmailVerifyView, EmailVerifyResendView,
)

user_router = DefaultRouter()
user_router.register("", ManageUserView, basename="me")

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainCookiePairView.as_view(), name="token"),
    path(
        "token/refresh/",
        TokenRefreshCookieView.as_view(),
        name="token_refresh",
    ),
    path("verify-email/", EmailVerifyView.as_view(), name="verify_email"),
    path("verify-resend/", EmailVerifyResendView.as_view(), name="verify_resend"),
    path("", include(user_router.urls)),
]

app_name = "user"
