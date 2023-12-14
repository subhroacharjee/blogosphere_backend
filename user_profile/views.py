from django.core.paginator import Paginator
from django.db.models import F, Q
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from user_profile.models import BlockList, Follows, Profile

from user_profile.serializer import (
    ProfileBlockingSerializer,
    ProfileInfoSerializer,
    ProfileSearchSerializer,
    ProfileSerializer,
)


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
        profile = get_object_or_404(
            Profile,
            ~Q(blocker__blockee=request.user.profile),
            slug=slug,
            user__is_active=True,
        )

        data = None
        rel = None
        if rel is None:
            # further fetch more data
            pass
        else:
            # only use ProfileSerializer
            pass

        return Response(
            {
                "data": ProfileSerializer(profile).data,
            }
        )


class UserProfileToggleFollowView(APIView):
    def post(self, request, slug):
        profile = get_object_or_404(
            Profile,
            ~Q(
                blocker__blockee=request.user.profile,
            ),
            slug=slug,
            user__is_active=True,
        )
        follower = request.user.profile
        rel = Follows.objects.filter(follower=follower, followee=profile).first()  # type: ignore
        is_deleted = False

        if rel is None:
            rel = Follows(follower=request.user.profile, followee=profile)
            rel.save()
        else:
            is_deleted = True
            rel.delete()
        return Response(
            {
                "data": f"{'unfollowed' if is_deleted else 'followed' }",
            }
        )


class UserProfileSearchView(APIView):
    def post(self, request):
        serializer = ProfileSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profiles = Profile.objects.filter(  # type:ignore
            Q(slug__icontains=serializer.validated_data.get("search_key"))  # type:ignore
            & Q(user__is_active=True)
            & ~Q(blocker__blockee=request.user.profile)
            & ~Q(blocking__blocker=request.user.profile)
        ).exclude(pk=request.user.profile.pk)
        paginator = Paginator(profiles, 10)
        page = request.query_params.get("page", 1)
        profiles = paginator.get_page(page)
        return Response({"data": ProfileInfoSerializer(profiles, many=True).data})


class ToggleBlockProfileView(APIView):
    def delete(self, request, slug):
        serializer = ProfileBlockingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_profile = request.user.profile
        profile = get_object_or_404(
            Profile,
            ~Q(pk=current_profile.pk),
            slug=slug,
            user__is_active=True,
        )

        rel = BlockList.objects.filter(  # type: ignore
            blocker=current_profile,
            blockee=profile,
        ).first()

        if rel is None:
            rel = BlockList(
                blocker=current_profile,
                blockee=profile,
                reason=serializer.validated_data.get("reason"),  # type:ignore
            )
            rel.save()
        else:
            rel.delete()

        return Response(
            {
                "data": "operation complete!",
            }
        )


class BlockListPreviewView(APIView):
    def get(self, request):
        serializers = ProfileSerializer(
            request.user.profile.block_list,
            many=True,
        )
        return Response(
            {
                "data": serializers.data,
            }
        )
