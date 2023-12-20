from uuid import uuid4

from faker import Faker


def create_user_data():
    fake = Faker()
    return {
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
