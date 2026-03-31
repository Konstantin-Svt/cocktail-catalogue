from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.db import transaction
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.serializers import CreateUserSerializer, ManageUserSerializer
from user.tasks import send_verification_email


class CreateUserView(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
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
                if not user.email_verified:
                    for key, value in serializer.validated_data.items():
                        if key == "password":
                            user.set_password(value)
                        else:
                            setattr(user, key, value)
                    user.save()
                    send_verification_email.delay_on_commit(user.pk)
                else:
                    pass
            else:
                new_user = serializer.save()
                send_verification_email.delay_on_commit(new_user.pk)

        return Response(
            {"detail": "Verification link has been send to email."},
            status=status.HTTP_201_CREATED,
        )


class ManageUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ManageUserSerializer

    def get_object(self):
        return (
            get_user_model()
            .objects.prefetch_related("favourite_cocktails")
            .get(pk=self.request.user.pk)
        )


class TokenObtainCookiePairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        if serializer.user.email_verified is False:
            send_verification_email.delay(serializer.user.pk)
            return Response(
                {
                    "detail": "Email is not verified. Verification link has been sent to email."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            access_token = serializer.validated_data["access"]
            refresh_token = serializer.validated_data["refresh"]
            response = Response(
                {"detail": "Login was successful."}, status=status.HTTP_200_OK
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
            {"detail": "access token refreshed successfully."},
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

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        uid = request.query_params.get("uid")
        if not token or not uid:
            raise ValidationError("Link is invalid.")
        try:
            user_id = signing.loads(uid, salt="email-confirmation-id")
            user = get_user_model().objects.get(pk=user_id)
        except (signing.BadSignature, get_user_model().DoesNotExist):
            raise ValidationError("Link is invalid.")
        if default_token_generator.check_token(user, token) is not True:
            raise ValidationError("Link is invalid.")

        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        response = Response(
            {"detail": "Email successfully verified."},
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
