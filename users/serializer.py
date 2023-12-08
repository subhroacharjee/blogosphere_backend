from typing import cast
from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.models import User

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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
