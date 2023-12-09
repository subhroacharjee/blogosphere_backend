from typing import cast
from uuid import uuid4
from django.db.models import Q, QuerySet
from django.utils.timezone import now, timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from users.models import User, VerifyToken
from users.utils import create_token_and_send_verify_email

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            "email",
            "username",
            "slug",
            "avatar",
            "description",
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

    def update(self, instance: User, validated_data):
        new_password = validated_data.pop("password", None)
        username = validated_data.get("username", None)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.description = validated_data.get("description", instance.description)

        if new_password:
            instance.set_password(new_password)

        if username:
            instance.username = username
            instance.slug = None  # type: ignore

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
            )

        except Exception as e:
            print(e)
            raise APIException("Invalid token", code=HTTP_400_BAD_REQUEST)

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
            raise APIException("Invalid input", code=HTTP_400_BAD_REQUEST)

        return validated_data
