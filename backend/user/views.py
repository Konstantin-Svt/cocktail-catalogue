from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.db import transaction
from django.db.models import Prefetch
from django.urls import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from analytics.services import (
    signup_analytics_wrapper,
    login_analytics_wrapper,
    logout_analytics_wrapper,
)
from catalogue_system.pagination import StandardResultsSetPagination
from cocktail.models import Cocktail
from cocktail.serializers import (
    FavCocktailIdSerializer,
    CocktailListSerializer,
)
from user.authentication import EmailVerificationTokenGenerator
from user.serializers import (
    CreateUserSerializer,
    ManageUserSerializer,
    ChangePasswordSerializer,
    EmailSerializer,
    ChangeEmailSerializer,
    ResetPasswordSerializer,
    PasswordSerializer,
)
from user.tasks import (
    send_verification_email,
    send_change_email,
    send_reset_password_email,
)

email_token_generator = EmailVerificationTokenGenerator()


class CreateUserView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        """
        Endpoint to create a new user. If user with that email already exists
        and email is not verified, sends verification email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        with transaction.atomic():
            user = (
                get_user_model()
                .objects.select_for_update()
                .filter(
                    email=email,
                )
                .first()
            )
            if user:
                if not user.can_send_mail():
                    return Response(
                        {"detail": "You need to wait."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
                if user.email_verified is True:
                    raise ValidationError(
                        {"email": "This email address is already taken."}
                    )
                if user.is_active is True:
                    send_verification_email.delay_on_commit(user.pk)
                    raise ValidationError(
                        {
                            "email": "This email address is already taken, "
                            "but unverified. If it is your email, check inbox."
                        }
                    )

                for key, value in serializer.validated_data.items():
                    if key == "password":
                        user.set_password(value)
                    else:
                        setattr(user, key, value)
                user.is_active = True
                user.save()
            else:
                user = serializer.save()

        send_verification_email.delay_on_commit(user.pk)
        if settings.AUTO_VERIFY_EMAIL:
            signup_analytics_wrapper(request, user.pk)
            return Response(
                {"detail": "User is successfully created."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Verification link has been send to email."},
            status=status.HTTP_201_CREATED,
        )


class ManageUserView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "change_password":
            return ChangePasswordSerializer
        if self.action == "change_email":
            return ChangeEmailSerializer
        if self.action in ("change_email_verify", "logout"):
            return Serializer
        if self.action in (
            "add_favourite_cocktail",
            "remove_favourite_cocktail",
        ):
            return FavCocktailIdSerializer
        if self.action == "delete_account":
            return PasswordSerializer
        return ManageUserSerializer

    def get_queryset(self):
        if self.action == "favourite_cocktails":
            return (
                Cocktail.objects.with_levels()
                .filter(
                    pk__in=self.request.user.favourite_cocktails.values_list(
                        "pk", flat=True
                    )
                )
                .prefetch_related("vibes", "ingredients")
                .order_by("name")
                .distinct()
            )
        return (
            get_user_model()
            .objects.prefetch_related(
                Prefetch(
                    "favourite_cocktails", queryset=Cocktail.objects.only("id")
                )
            )
            .get(pk=self.request.user.pk)
        )

    def get_object(self):
        return self.get_queryset()

    @action(
        detail=False,
        methods=["post"],
        url_path="delete",
        serializer_class=PasswordSerializer,
    )
    def delete_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = (
                get_user_model()
                .objects.filter(pk=request.user.pk)
                .select_for_update()
                .first()
            )
            if not user:
                raise ValidationError({"detail": "User not found."})
            if not user.check_password(serializer.validated_data["password"]):
                raise ValidationError({"password": "Incorrect password."})
            user.is_active = False
            user.email_verified = False
            user.save()

        res = Response(
            {"detail": "User successfully deleted."}, status=status.HTTP_200_OK
        )
        res.delete_cookie("access_token", path="/api/")
        res.delete_cookie(
            "refresh_token", path=str(reverse("user:token_refresh"))
        )
        return res

    @extend_schema(responses=CocktailListSerializer)
    @action(
        detail=False,
        methods=["get"],
        url_path="favourites",
        serializer_class=CocktailListSerializer,
        pagination_class=StandardResultsSetPagination,
    )
    def favourite_cocktails(self, request, *args, **kwargs):
        serializer = CocktailListSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="add-favourites",
        serializer_class=FavCocktailIdSerializer,
    )
    def add_favourite_cocktail(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.favourite_cocktails.add(serializer.validated_data["cocktail_id"])
        return Response(
            {"detail": "Cocktail successfully added to favourites."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="remove-favourites",
        serializer_class=FavCocktailIdSerializer,
    )
    def remove_favourite_cocktail(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.favourite_cocktails.remove(
            serializer.validated_data["cocktail_id"]
        )
        return Response(
            {"detail": "Cocktail successfully removed from favourites."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
        serializer_class=ChangePasswordSerializer,
    )
    def change_password(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            raise ValidationError({"old_password": "Wrong password."})
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response(
            {"detail": "Password successfully changed."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="change-email",
        serializer_class=ChangeEmailSerializer,
    )
    def change_email(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["password"]):
            raise ValidationError({"password": "Wrong password."})

        new_email = serializer.validated_data["new_email"]
        if user.email == new_email:
            raise ValidationError(
                {"new_email": "New email is your current email."}
            )

        if not user.can_send_mail():
            return Response(
                {"detail": "You need to wait."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if get_user_model().objects.filter(email=new_email).exists():
            raise ValidationError(
                {"new_email": "This email address is already taken."},
            )

        send_change_email.delay(
            user.pk,
            new_email,
        )
        return Response(
            {"detail": "Verification link has been send to the new email."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="uid",
                type=str,
                description="Identifier of the user, "
                "resend from mail verification link",
                many=False,
                required=True,
            ),
            OpenApiParameter(
                name="token",
                type=str,
                description="Token of the user, "
                "resend from mail verification link",
                many=False,
                required=True,
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="change-email-verify",
        serializer_class=None,
    )
    def change_email_verify(self, request, pk=None):
        """
        Requires being authenticated!!!
        Endpoint to verify changing email address. Requires q_params
        'token' and 'uid' from verification link sent to email.
        """
        token = request.query_params.get("token")
        uid = request.query_params.get("uid")
        if not token or not uid:
            raise ValidationError("Link is invalid.")
        try:
            user_id, new_email = signing.loads(
                uid,
                salt="email-change-id",
                max_age=settings.EMAIL_VERIFY_RESET_TIMEOUT,
            )
        except signing.BadSignature:
            raise ValidationError("Link is invalid.")
        with transaction.atomic():
            user = (
                get_user_model()
                .objects.select_for_update()
                .filter(pk=user_id)
                .first()
            )
            existing_user = (
                get_user_model()
                .objects.select_for_update()
                .filter(email=new_email)
                .first()
            )
            if (
                existing_user
                or not user
                or not email_token_generator.check_token(user, token)
            ):
                raise ValidationError("Link is invalid.")

            user.email = new_email
            user.save(update_fields=["email"])

        return Response(
            {"detail": "Email changed successfully.", "email": new_email},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        serializer_class=None,
    )
    def logout(self, request):
        """
        Send empty post to logout and delete both tokens from cookies.
        """
        logout_analytics_wrapper(request)

        res = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )
        res.delete_cookie("access_token", path="/api/")
        res.delete_cookie(
            "refresh_token", path=str(reverse("user:token_refresh"))
        )
        return res


class TokenObtainCookiePairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            login_analytics_wrapper(request)
            raise InvalidToken(e.args[0]) from e

        if serializer.user.email_verified is False:
            login_analytics_wrapper(request)
            send_verification_email.delay(serializer.user.pk)
            return Response(
                {
                    "detail": "Email is unverified. Verification link has been sent to your email."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        login_analytics_wrapper(request, serializer.user.pk)

        access_token = serializer.validated_data["access"]
        refresh_token = serializer.validated_data["refresh"]
        response = Response(
            {
                "detail": "Login was successful.",
                "access": access_token,
                "refresh": refresh_token,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "access_token",
            access_token,
            max_age=settings.SIMPLE_JWT[
                "ACCESS_TOKEN_LIFETIME"
            ].total_seconds(),
            secure=not settings.DEBUG,
            httponly=True,
            samesite="Lax" if settings.DEBUG else "None",
            path="/api/",
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.SIMPLE_JWT[
                "REFRESH_TOKEN_LIFETIME"
            ].total_seconds(),
            secure=not settings.DEBUG,
            httponly=True,
            samesite="Lax" if settings.DEBUG else "None",
            path=str(reverse("user:token_refresh")),
        )
        return response


class TokenRefreshCookieView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        """
        Endpoint to refresh access token. Either send empty post request if refresh token
        is in cookies or send refresh token value in body to get a new access token,
        which is returned both in cookies and response field.
        """
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is absent."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        data = {"refresh": refresh_token}
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        access_token = serializer.validated_data["access"]
        response = Response(
            {
                "detail": "access token refreshed successfully.",
                "access": access_token,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "access_token",
            access_token,
            max_age=settings.SIMPLE_JWT[
                "ACCESS_TOKEN_LIFETIME"
            ].total_seconds(),
            secure=not settings.DEBUG,
            httponly=True,
            samesite="Lax" if settings.DEBUG else "None",
            path="/api/",
        )

        return response


class EmailVerifyView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("GET",)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="uid",
                type=str,
                description="Identifier of the user, "
                "resend from mail verification link",
                many=False,
                required=True,
            ),
            OpenApiParameter(
                name="token",
                type=str,
                description="Token of the user, "
                "resend from mail verification link",
                many=False,
                required=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Endpoint to verify email address. Requires q_params 'token' and 'uid' from
        verification link sent to email. If the user exists,
        automatically creates JWT tokens, puts them in cookies and logins the user.
        """
        token = request.query_params.get("token")
        uid = request.query_params.get("uid")
        if not token or not uid:
            raise ValidationError("Link is invalid.")

        try:
            user_id = signing.loads(
                uid,
                salt="email-confirmation-id",
                max_age=settings.EMAIL_VERIFY_RESET_TIMEOUT,
            )
            user = get_user_model().objects.get(pk=user_id)
        except (signing.BadSignature, get_user_model().DoesNotExist):
            signup_analytics_wrapper(request)
            raise ValidationError("Link is invalid.")
        if not email_token_generator.check_token(user, token):
            signup_analytics_wrapper(request)
            raise ValidationError("Link is invalid.")

        signup_analytics_wrapper(request, user.pk)
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        response = Response(
            {
                "detail": "Email successfully verified! "
                "You can come back now to registration page.",
                "access": str(access_token),
                "refresh": str(refresh_token),
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "access_token",
            str(access_token),
            max_age=settings.SIMPLE_JWT[
                "ACCESS_TOKEN_LIFETIME"
            ].total_seconds(),
            secure=not settings.DEBUG,
            httponly=True,
            samesite="Lax" if settings.DEBUG else "None",
            path="/api/",
        )
        response.set_cookie(
            "refresh_token",
            str(refresh_token),
            max_age=settings.SIMPLE_JWT[
                "REFRESH_TOKEN_LIFETIME"
            ].total_seconds(),
            secure=not settings.DEBUG,
            httponly=True,
            samesite="Lax" if settings.DEBUG else "None",
            path=str(reverse("user:token_refresh")),
        )

        return response


class EmailVerifyResendView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("POST",)

    @extend_schema(request=EmailSerializer)
    def post(self, request, *args, **kwargs):
        """
        Endpoint for requesting an email verification link to send again.
        """
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = (
            get_user_model()
            .objects.filter(email=serializer.validated_data["email"])
            .first()
        )
        if not user:
            raise ValidationError({"email": "No such email address."})

        if user.email_verified is True:
            raise ValidationError({"email": "Email already verified."})

        if not user.can_send_mail():
            return Response(
                {"detail": "You need to wait."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        send_verification_email.delay(user.pk)
        return Response(
            {"detail": "Verification link has been resend."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("POST",)

    @extend_schema(request=EmailSerializer)
    def post(self, request, *args, **kwargs):
        """
        Endpoint for requesting a password reset link being sent to email.
        """
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = (
            get_user_model()
            .objects.filter(email=serializer.validated_data["email"])
            .first()
        )
        if not user:
            raise ValidationError({"email": "No such email address."})

        if not user.can_send_mail():
            return Response(
                {"detail": "You need to wait."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        mail = send_reset_password_email.delay_on_commit(user.pk)
        if settings.AUTO_VERIFY_EMAIL:
            mail = mail.get()
            return Response({"link": mail}, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Reset password link has been send to email."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("POST",)

    @extend_schema(request=ResetPasswordSerializer)
    def post(self, request, *args, **kwargs):
        """
        Endpoint to set a new password after reset. Take 'uid' and 'token' from
        reset link q_params sent to email.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        try:
            user_id = signing.loads(
                uid,
                salt="password-reset-id",
                max_age=settings.PASSWORD_RESET_TIMEOUT,
            )
            user = get_user_model().objects.get(pk=user_id)
        except (signing.BadSignature, get_user_model().DoesNotExist):
            raise ValidationError("Link is invalid.")
        if not default_token_generator.check_token(user, token):
            raise ValidationError("Link is invalid.")

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(
            {"detail": "Password has been successfully changed."},
            status=status.HTTP_200_OK,
        )


class UnsubscribeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Unsubscribed"})
