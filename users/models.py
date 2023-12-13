from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if email is None:
            raise ValueError("User must have a email address")
        if username is None:
            raise ValueError("User must have a username")

        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save(self._db)
        return user

    pass

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email, username=username, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(self._db)
        return user

    pass


class User(AbstractBaseUser):
    email = models.EmailField(null=False, unique=True)
    username = models.CharField(max_length=30, null=False, unique=True)
    password = models.CharField(max_length=100, null=False)

    is_active = models.BooleanField(default=False)  # type: ignore
    is_admin = models.BooleanField(default=False)  # type: ignore
    is_staff = models.BooleanField(default=True)  # type: ignore
    is_superuser = models.BooleanField(default=False)  # type: ignore

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perm(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.profile.slug = None  # type: ignore
            if "ui-avatars.com/api/" in self.profile.avatar:  # type: ignore
                self.avatar = None
            self.profile.save()  # type: ignore
        return super().save(*args, **kwargs)

    pass


class VerifyToken(models.Model):
    TOKEN_TYPES = (
        ("F", "forget_password"),
        ("V", "verify_user"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)  # type: ignore
    used_for = models.CharField(max_length=1, choices=TOKEN_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.token + " " + str(self.expires_at)  # type: ignore
