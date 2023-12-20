from typing import cast

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from users.models import User, VerifyToken
from users.utils import create_token_and_send_verify_email

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        validators=[validate_password],
        write_only=True,
    )

    class Meta:
        model = UserModel
        fields = (
            "email",
            "username",
            "created_at",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = cast(User, self.Meta.model(**validated_data))
        if password is not None:
            instance.set_password(password)
        else:
            raise Exception("password cant be None")
        instance.save()
        return instance


class UserActivationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        try:
            token = VerifyToken.objects.get(  # type: ignore
                Q(token__exact=validated_data.get("token"))  # type: ignore
                & Q(expires_at__gt=now())
                & Q(is_used__exact=False)
                & Q(used_for__exact="V")
            )

        except ObjectDoesNotExist:
            raise serializers.ValidationError("invalid token")

        token = cast(VerifyToken, token)
        token.user.is_active = True  # type: ignore
        token.is_used = True  # type: ignore
        token.user.save()  # type: ignore
        token.save()

        return validated_data


class UserReactivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        try:
            user = User.objects.get(
                Q(is_active__exact=False) & Q(email__exact=validated_data.get("email"))
            )
            user.verifytoken_set.filter().update(is_used=True)
            create_token_and_send_verify_email(user)
            pass
        except Exception as e:
            print(e)

        return validated_data


class UserForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        print(validated_data)
        try:
            user = User.objects.get(
                Q(is_active__exact=True) & Q(email__exact=validated_data.get("email"))
            )
            user.verifytoken_set.filter().update(is_used=True)
            create_token_and_send_verify_email(user, "F")
            pass
        except Exception as e:
            print(e)
            raise serializers.ValidationError("no such user found!")

        return validated_data


class UserForgetVerifySerializer(serializers.Serializer):
    class Meta:
        model = UserModel

    token = serializers.UUIDField()
    new_password = serializers.CharField(
        max_length=100,
        min_length=8,
        validators=[validate_password],
    )

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        try:
            token = VerifyToken.objects.get(  # type: ignore
                Q(token__exact=validated_data.get("token"))  # type: ignore
                & Q(expires_at__gt=now())
                & Q(is_used__exact=False)
                & Q(used_for__exact="F")
            )
            pass
        except Exception as e:
            print(e)
            raise serializers.ValidationError("invalid token")

        token = cast(VerifyToken, token)
        token.user.set_password(validated_data.get("new_password"))  # type: ignore
        token.user.save()  # type: ignore
        token.is_used = True  # type: ignore
        token.save()

        return validated_data


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=100,
        min_length=8,
    )

    new_password = serializers.CharField(
        max_length=100,
        min_length=8,
        validators=[validate_password],
    )


class UserBasicChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            "username",
            "email",
        )
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            "email": {"required": False, "allow_blank": True},
        }

    def update(self, instance: User, validated_data):
        username = validated_data.get("username", None)

        email = validated_data.get("email", None)

        if username:
            instance.username = username

        if email:
            instance.email = email

        instance.save()
        return instance
