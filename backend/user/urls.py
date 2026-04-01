from django.urls import path

from user.views import (
    ManageUserView,
    CreateUserView,
    TokenObtainCookiePairView,
    TokenRefreshCookieView,
    EmailVerifyView, VerifyEmailResendView,
)

urlpatterns = [
    path("me/", ManageUserView.as_view(), name="me"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainCookiePairView.as_view(), name="token"),
    path(
        "token/refresh/",
        TokenRefreshCookieView.as_view(),
        name="token_refresh",
    ),
    path("verify-email/", EmailVerifyView.as_view(), name="verify_email"),
    path("verify-resend/", VerifyEmailResendView.as_view(), name="verify_resend"),
]

app_name = "user"
