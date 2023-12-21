from operator import indexOf
from typing import cast
from uuid import uuid4
from django.urls import reverse
from faker import Faker
from rest_framework.exceptions import status
from rest_framework.test import APIClient, APITestCase
from users.models import User

from users.tests.utils import create_user_data


class TestUserBasicDetailsView(APITestCase):
    url = reverse("change_data")
    fake = Faker()

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

    def test_fails_when_username_already_exists(self):
        existing_user_name = "i_exists"
        new_user = User(
            username=existing_user_name,
            email=self.fake.email(),
        )
        new_user.set_password("Val1d_Passw0rd")
        new_user.save()

        response = self.client.post(
            self.url,
            {
                "username": existing_user_name,
            },
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )
        pass

    def test_fails_when_invalid_email(self):
        response = self.client.post(
            self.url,
            {
                "email": "invalid_mail",
            },
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )

        pass

    def test_fails_when_email_exists(self):
        existing_email = "i_exists@email.com"
        new_user = User(
            username=self.fake.name(),
            email=existing_email,
        )
        new_user.set_password("Val1d_Passw0rd")
        new_user.save()

        response = self.client.post(
            self.url,
            {
                "email": existing_email,
            },
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )
        pass

    def test_basic_data_changes_when_successful(self):
        changes = {
            "change_username": {
                "username": uuid4(),
            },
            "change_email": {"email": f"{uuid4()}_{self.fake.email()}"},
        }

        for key, payload in changes.items():
            response = self.client.post(self.url, payload)
            self.assertEqual(
                response.status_code,  # type: ignore
                status.HTTP_200_OK,
                msg=key,
            )
            user = User.objects.get(pk=self.user_pk)
            if key.find("username") != -1:
                self.assertEqual(user.username, f"{payload['username']}", msg=key)
            else:
                self.assertEqual(user.email, payload["email"], msg=key)

        pass
