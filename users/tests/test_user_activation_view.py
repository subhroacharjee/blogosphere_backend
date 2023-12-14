from uuid import uuid4
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from faker import Faker

from users.models import User, VerifyToken


class TestUserActivationView(APITestCase):
    url = reverse("activate_user")

    @classmethod
    def setUpClass(cls):
        super(TestUserActivationView, cls).setUpClass()
        fake = Faker()
        user_data = {
            "username": uuid4(),
            "email": fake.email(),
            "password": fake.password(
                length=10,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
        }
        response = APIClient().post(
            reverse("register"),
            user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore
        cls.user_data = user_data

    def test_activation_fails_when_incorrect_uuid(self):
        response = self.client.post(
            self.url,
            {
                "token": "invalid_uuid",
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_is_active_when_correct_uuid(self):
        user = User.objects.get(username=self.user_data["username"])
        self.assertFalse(user.is_active)

        token = VerifyToken.objects.filter(  # type: ignore
            user=user,
            used_for="V",
        ).first()
        self.assertIsNot(token, None)

        response = self.client.post(self.url, {"token": token.token})
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_200_OK,
        )
        user = User.objects.get(username=self.user_data["username"])
        self.assertTrue(user.is_active)
        self._test_activation_throws_error_when_activating_active_user()

    def _test_activation_throws_error_when_activating_active_user(self):
        user = User.objects.get(username=self.user_data["username"])
        self.assertTrue(user.is_active)

        token = VerifyToken.objects.filter(  # type: ignore
            user=user,
            used_for="V",
        ).first()
        self.assertIsNot(token, None)
        self.assertTrue(token.is_used)

        response = self.client.post(
            self.url,
            {
                "token": token.token,
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )
