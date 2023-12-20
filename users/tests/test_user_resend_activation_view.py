from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import VerifyToken
from users.tests.utils import create_user_data


class TestUserResendActivationView(APITestCase):
    url = reverse("refresh_again")

    @classmethod
    def setUpClass(cls):
        user_data = create_user_data()
        client = APIClient()
        response = client.post(
            reverse("register"),
            data=user_data,
        )

        assert response.status_code == status.HTTP_201_CREATED  # type: ignore

        cls.user_data = user_data
        return super().setUpClass()

    def test_resend_activation_fails_when_invalid_email(self):
        response = self.client.post(
            self.url,
            {
                "email": "invalid_email",
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )

    def test_resend_activation_fails_silently_when_email_doest_exists(self):
        response = self.client.post(
            self.url,
            {"email": "my_absurdly_long_email_that_should_be_super_unique@yopmail.com"},
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_200_OK,
        )

    def test_old_activation_token_is_marked_used_when_new_token_is_requested(self):
        old_token = VerifyToken.objects.filter(  # type: ignore
            user__username=self.user_data["username"],
            is_used=False,
            used_for="V",
        ).first()
        self.assertIsNot(old_token, None)
        self.assertFalse(old_token.is_used)

        response = self.client.post(
            self.url,
            {
                "email": self.user_data["email"],
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_200_OK,
        )

        old_token = VerifyToken.objects.get(  # type: ignore
            pk=old_token.pk,
        )
        self.assertTrue(old_token.is_used)
