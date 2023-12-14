from typing import cast
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from rest_framework_simplejwt.views import TokenObtainPairView
from user_profile.models import Profile
from users.models import User

from users.serializer import (
    UserActivationSerializer,
    UserBasicChangeSerializer,
    UserChangePasswordSerializer,
    UserForgetPasswordSerializer,
    UserForgetVerifySerializer,
    UserReactivationSerializer,
    UserSerializer,
)
from users.utils import create_token_and_send_verify_email


class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.profile = Profile()
        user.profile.save()
        create_token_and_send_verify_email(user)
        return Response(
            {
                "data": "verification mail has been sent!",
            },
            status.HTTP_201_CREATED,
        )


class UserLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = serializer.user
        data = serializer.validated_data
        return Response(
            {
                "data": {
                    "user": UserSerializer(user).data,
                    "tokens": data,
                }
            },
            HTTP_200_OK,
        )


class UserActivationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "data": "your account is activated!",
            },
            HTTP_200_OK,
        )


class UserResendActivationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserReactivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": "verification mail has been sent!"})


class UserForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": "verification mail has been sent!"})


class UserForgetPasswordVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserForgetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": "new password has been set. please login"})


class UserChangePasswordView(APIView):
    def post(self, request):
        current_user = cast(User, request.user)
        serializer = UserChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not current_user.check_password(
            serializer.validated_data.get("old_password")  # type: ignore
        ):
            raise APIException(
                detail="Invalid old password", code=HTTP_401_UNAUTHORIZED
            )

        current_user.set_password(serializer.validated_data.get("new_password"))  # type: ignore
        current_user.save()
        return Response(
            {
                "data": "password has been set",
            },
            HTTP_200_OK,
        )


class UserChangeBasicDetails(APIView):
    def post(self, request):
        serializer = UserBasicChangeSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "data": serializer.data,
            }
        )
