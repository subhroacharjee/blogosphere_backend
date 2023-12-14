from django.contrib.auth import get_user_model
from rest_framework import serializers

from user_profile.models import Profile


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username",)


class ProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "slug",
            "avatar",
        )


class ProfileSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    followers = ProfileInfoSerializer(read_only=True, many=True)
    followings = ProfileInfoSerializer(read_only=True, many=True)

    class Meta:
        model = Profile
        fields = (
            "slug",
            "avatar",
            "description",
            "user",
            "cover_pic",
            "followers",
            "followings",
        )

        extra_kwargs = {
            "user": {"read_only": True},
            "slug": {"read_only": True},
        }

    def update(self, instance, validated_data):
        instance.description = validated_data.get("description", instance.description)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class ProfileSearchSerializer(serializers.Serializer):
    search_key = serializers.CharField(max_length=200, min_length=2)


class ProfileBlockingSerializer(serializers.Serializer):
    reason = serializers.CharField(
        max_length=200,
        allow_null=True,
        required=False,
        allow_blank=True,
    )
