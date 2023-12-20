from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.models import User, VerifyToken

from users.tests.utils import create_user_data


class TestForgetPasswordVerifyView(APITestCase):
    url = reverse("forget_password_verify")

    @classmethod
    def setUpClass(cls):
        client = APIClient()
        user_data = create_user_data()
        response = client.post(reverse("register"), user_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore

        new_user = User.objects.filter(username=user_data["username"]).first()
        assert new_user is not None

        new_user.is_active = True  # type: ignore
        new_user.save()

        response = client.post(reverse("forget_password"), user_data)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

        cls.user = new_user
        verification_token = VerifyToken.objects.filter(  # type: ignore
            user=new_user,
            used_for="F",
            is_used=False,
        ).first()

        assert verification_token is not None
        cls.valid_token = verification_token.token
        return super().setUpClass()

    def test_verify_forget_password_fails_when_invalid_data(self):
        invalid_datas = {
            "no_token": {
                "token": "",
                "new_password": "a_good_password@123",
            },
            "invalid_token": {
                "token": "thisisinvalidtoken",
                "new_password": "a_good_password@123",
            },
            "invalid_password_less_than_8": {
                "token": self.valid_token,
                "new_password": "goku",
            },
            "invalid_password_common_password": {
                "token": self.valid_token,
                "new_password": "password",
            },
            "invalid_password_all_numeric": {
                "token": self.valid_token,
                "new_password": "123456789",
            },
        }

        for key, payload in invalid_datas.items():
            response = self.client.post(self.url, payload)
            self.assertEqual(
                response.status_code,  # type: ignore
                status.HTTP_400_BAD_REQUEST,
                msg=key,
            )

    def test_password_should_update_when_verification_is_successful(self):
        new_password = "A_g00d_password@123"
        response = self.client.post(
            self.url,
            {
                "token": self.valid_token,
                "new_password": new_password,
            },
        )
        self.assertEqual(
            response.status_code,  # type: ignore
            status.HTTP_200_OK,
        )
        user = User.objects.get(pk=self.user.pk)

        self.assertTrue(user.check_password(new_password))
