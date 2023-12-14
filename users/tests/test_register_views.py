from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status

from rest_framework.test import APITestCase
from user_profile.models import Profile

from users.models import User, VerifyToken


class TestUserRegisterView(APITestCase):
    url = reverse("register")

    def test_registration_should_fail_when_invalid_data(self):
        invalid_datas = {
            "invalid_username": {
                "username": "",
                "email": "some@email.com",
                "password": "Password@123",
            },
            "invalid_email": {
                "username": "valid_user_name",
                "email": "notanemail",
                "password": "somePassword",
            },
            "invalid_password_length_less_than_8": {
                "username": "valid_user_name",
                "email": "some@email.com",
                "password": "goku",
            },
            "invalid_password_common_password": {
                "username": "valid_user_name",
                "email": "some@email.com",
                "password": "password",
            },
            "invalid_password_all_numeric": {
                "username": "valid_user_name",
                "email": "some@email.com",
                "password": "1234578",
            },
        }
        for key, data in invalid_datas.items():
            response = self.client.post(
                self.url,
                data,
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=key)  # type: ignore

    def test_registration_fails_when_email_already_exists(self):
        new_user = User(
            username="user1",
            email="user1@email.com",
        )
        new_user.set_password("ValidPass123")
        new_user.save()

        response = self.client.post(
            self.url,
            {
                "username": "user2",
                "email": "user1@email.com",
                "password": "ValidPass123",
            },
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )
        pass

    def test_registration_fails_when_username_already_exists(self):
        new_user = User(
            username="user2",
            email="user2@email.com",
        )
        new_user.set_password("ValidPass123")
        new_user.save()

        response = self.client.post(
            self.url,
            {
                "username": "user2",
                "email": "user3@email.com",
                "password": "ValidPass123",
            },
        )

        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_400_BAD_REQUEST,
        )

        pass

    def test_verification_code_created_when_registration_successful(self):
        response = self.client.post(
            self.url,
            {
                "username": "valid_user_name",
                "email": "some@email.com",
                "password": "Should_be_valid_password_123",
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_201_CREATED,
            msg=response.data,  # type: ignore
        )

        verify_token = VerifyToken.objects.filter(  # type: ignore
            user__username="valid_user_name",
            used_for="V",
        ).first()
        self.assertIsNot(verify_token, None)
        self.assertFalse(verify_token.is_used)
        self.assertLessEqual(verify_token.expires_at, now() + timedelta(hours=1))

    def test_profile_created_when_registration_successful(self):
        response = self.client.post(
            self.url,
            {
                "username": "valid_user_name",
                "email": "some@email.com",
                "password": "Should_be_valid_password_123",
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_201_CREATED,
            msg=response.data,  # type: ignore
        )

        profile = Profile.objects.filter(  # type: ignore
            user__username="valid_user_name",
        ).first()

        self.assertIsNot(profile, None)
