from typing import cast
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.models import User

from users.tests.utils import create_user_data


class TestUserChangePasswordView(APITestCase):
    url = reverse("change_password")

    @classmethod
    def setUpClass(cls):
        user_data = create_user_data()
        client = APIClient()

        response = client.post(reverse("register"), user_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore

        user = User.objects.get(username=user_data["username"])
        user.is_active = True
        user.save()

        response = client.post(reverse("login"), user_data)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

        response_data = cast(dict, response.data["data"])  # type: ignore
        # print(response_data)
        token = cast(str, response_data["tokens"]["access"])

        assert len(token) != 0
        cls.access_token = token
        cls.client = client
        cls.user_pk = user.pk
        cls.user_data = user_data
        return super().setUpClass()

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        return super().setUp()

    def test_change_password_fails_when_incorrect_old_password(self):
        response = self.client.post(
            self.url,
            {"old_password": "invalid_old_password", "new_password": "Val1d_passw0rd"},
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_401_UNAUTHORIZED,
            msg=response.data,  # type: ignore
        )
        pass

    def test_change_password_fails_when_invalid_new_password(self):
        invalid_passwords = {
            "invalid_password_less_than_8": {
                "old_password": self.user_data["password"],
                "new_password": "goku",
            },
            "invalid_password_common_password": {
                "old_password": self.user_data["password"],
                "new_password": "password",
            },
            "invalid_password_all_numeric": {
                "old_password": self.user_data["password"],
                "new_password": "123456789",
            },
        }

        for key, payload in invalid_passwords.items():
            response = self.client.post(self.url, payload)
            self.assertEqual(
                response.status_code,  # type: ignore
                status.HTTP_400_BAD_REQUEST,
                msg=key,
            )
        pass

    def test_password_changes_when_successful(self):
        new_password = "AStr0ngPassw0rd_"
        response = self.client.post(
            self.url,
            {
                "old_password": self.user_data["password"],
                "new_password": new_password,
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_200_OK,
        )

        user = User.objects.get(pk=self.user_pk)
        self.assertTrue(user.check_password(new_password))
        pass
