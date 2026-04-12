from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import PasswordValidator


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[PasswordValidator()],
    )

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "gender",
            "country",
        )

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class ManageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "gender",
            "country",
            "email_verified",
            "favourite_cocktails",
        )
        read_only_fields = ("id", "email_verified", "email", "favourite_cocktails")

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            "first_name", instance.first_name
        )
        instance.last_name = validated_data.get(
            "last_name", instance.last_name
        )
        instance.gender = validated_data.get("gender", instance.gender)
        instance.country = validated_data.get("country", instance.country)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[PasswordValidator()],
    )


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False)


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField(allow_null=False, allow_blank=False)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[PasswordValidator()],
    )
    uid = serializers.CharField(allow_blank=False, allow_null=False)
    token = serializers.CharField(allow_blank=False, allow_null=False)
