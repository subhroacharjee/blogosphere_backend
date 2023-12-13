from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from user_profile.models import Profile

from user_profile.serializer import ProfileSearchSerializer, ProfileSerializer


class CurrentProfileView(APIView):
    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(
            {
                "data": serializer.data,
            }
        )

    def put(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "data": serializer.data,
            }
        )


class UserProfileView(APIView):
    def get(self, request, slug):
        profile = get_object_or_404(Profile, slug=slug, user__is_active=True)
        return Response(
            {
                "data": ProfileSerializer(profile).data,
            }
        )


class UserProfileSearchView(APIView):
    def get(self, request):
        serializer = ProfileSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)

        profiles = Profile.objects.filter(  # type:ignore
            Q(slug__icontains=serializer.validated_data.get("search_key"))  # type:ignore
            & Q(user__is_active=True)
        ).exclude(pk=request.user.profile.pk)
        paginator = Paginator(profiles, 10)
        page = request.query_params.get("page", 1)
        profiles = paginator.get_page(page)
        return Response({"data": ProfileSerializer(profiles, many=True).data})
