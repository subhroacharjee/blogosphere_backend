from typing import cast
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.models import User
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializer import LoginSerializer, UserSerializer


class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # call email service to create a verfication mail with verification id
        return Response(
            {
                "data": serializer.data,
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
        print(user)
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
