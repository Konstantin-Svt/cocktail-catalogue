from django.urls import path

from user.views import (
    ManageUserView,
    CreateUserView,
    TokenObtainCookiePairView,
    TokenRefreshCookieView,
    EmailVerifyView,
    EmailVerifyResendView,
    ResetPasswordView,
    ResetPasswordConfirmView, UnsubscribeView,
)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainCookiePairView.as_view(), name="token"),
    path(
        "token/refresh/",
        TokenRefreshCookieView.as_view(),
        name="token_refresh",
    ),
    path("verify-email/", EmailVerifyView.as_view(), name="verify_email"),
    path(
        "verify-email-resend/",
        EmailVerifyResendView.as_view(),
        name="verify_resend",
    ),
    path(
        "reset-password/", ResetPasswordView.as_view(), name="reset_password"
    ),
    path(
        "reset-password-confirm/",
        ResetPasswordConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path("me/change-password/", ManageUserView.as_view({
        "post": "change_password"
    })),
    path("me/change-email/", ManageUserView.as_view({
        "post": "change_email"
    })),
    path("me/change-email-verify/", ManageUserView.as_view({
        "get": "change_email_verify"
    })),
    path("me/logout/", ManageUserView.as_view({
        "post": "logout"
    })),
    path("me/", ManageUserView.as_view({
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy"
    })),
]

app_name = "user"
