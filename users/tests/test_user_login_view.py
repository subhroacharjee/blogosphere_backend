from typing import cast
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.serializer import UserSerializer
from users.tests.utils import create_user_data


class TestUserLoginView(APITestCase):
    url = reverse("login")

    @classmethod
    def setUpClass(cls):
        user_data = create_user_data()

        new_user = User(email=user_data["email"], username=user_data["username"])
        new_user.set_password(user_data["password"])
        new_user.is_active = True  # type: ignore
        new_user.save()

        cls.user_data = user_data
        cls.user = new_user
        return super().setUpClass()

    def test_login_failed_when_email_invalid(self):
        invalid_datas = {
            "invalid_email": {
                "email": "some_invalid_email",
                "password": "password",
            },
            "email_doesnt_exisits": {
                "email": "some_random_email_should_not_exists@yopmail.com",
                "password": self.user_data["password"],
            },
        }

        for key, data in invalid_datas.items():
            response = self.client.post(self.url, data)
            self.assertEqual(
                response.status_code,  # type: ignore
                status.HTTP_401_UNAUTHORIZED,
                msg=key,
            )
        pass

    def test_login_failed_when_password_invalid(self):
        invalid_datas = {
            "invalid_password": {
                "email": self.user_data["email"],
                "password": "",
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
            "incorrect_password": {
                "email": self.user_data["email"],
                "password": "incorrect_password",
                "status_code": status.HTTP_401_UNAUTHORIZED,
            },
        }

        for key, data in invalid_datas.items():
            response = self.client.post(self.url, data)
            self.assertEqual(
                response.status_code,  # type: ignore
                data["status_code"],
                msg=key,
            )
        pass

    def test_recieve_user_data_and_tokens_when_login_successful(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_200_OK,
        )

        user_data = UserSerializer(self.user).data
        response_data = cast(dict, response.data["data"])  # type: ignore
        # print(type(response.data["data"]), response.data["data"])  # type: ignore
        self.assertDictEqual(response_data["user"], user_data)
        keys = list(response_data.keys())
        self.assertListEqual(["user", "tokens"], keys)
        keys = list(response_data["tokens"].keys())
        self.assertListEqual(["refresh", "access"], keys)

        pass
