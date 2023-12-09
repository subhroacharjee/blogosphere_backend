from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializer import (
    UserActivationSerializer,
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
        print(user)
        create_token_and_send_verify_email(user)
        return Response(
            {
                "data": "verification mail has been sent!",
            }
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


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response(
            {
                "data": {
                    "user": UserSerializer(user).data,
                }
            }
        )

    pass
