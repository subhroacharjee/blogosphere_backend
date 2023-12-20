from uuid import uuid4
from django.urls import reverse
from django.utils.timezone import now, timedelta, timezone
from rest_framework.exceptions import status
from rest_framework.test import APITestCase
from users.models import User, VerifyToken

from users.tests.utils import create_user_data


class TestUserForgetPasswordView(APITestCase):
    url = reverse("forget_password")

    @classmethod
    def setUpClass(cls):
        user_data = create_user_data()
        new_user = User(username=user_data["username"], email=user_data["email"])
        new_user.set_password(user_data["password"])
        new_user.is_active = True  # type: ignore
        new_user.save()

        new_token = VerifyToken(
            user=new_user,
            token=f"{uuid4()}",
            used_for="F",
            expires_at=now() + timedelta(hours=1),
        )
        new_token.save()
        new_token.save()
        cls.user_data = user_data
        cls.user = new_user
        cls.token = new_token
        return super().setUpClass()

    def test_forget_password_fails_when_invalid_email(self):
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
        pass

    def test_forget_password_should_fail_when_email_doesnt_exitst(self):
        response = self.client.post(
            self.url,
            {
                "email": "invalid_email@yopmail.com",
            },
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )
        pass

    def test_forget_password_should_create_token_when_email_is_valid(self):
        token = VerifyToken.objects.filter(  # type: ignore
            pk=self.token.pk,
        ).first()
        self.assertIsNotNone(token)
        self.assertFalse(token.is_used)
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

        token = VerifyToken.objects.filter(  # type: ignore
            pk=self.token.pk, is_used=False
        ).first()
        self.assertIsNone(token)

        new_token_count = VerifyToken.objects.filter(  # type: ignore
            user=self.user, used_for="F", is_used=False
        ).count()
        self.assertEqual(new_token_count, 1)
        pass
