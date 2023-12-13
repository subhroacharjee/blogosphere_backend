from rest_framework import serializers

from user_profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("slug", "avatar", "description", "user", "cover_pic")

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
