from urllib import parse
from django.db import models
from django.utils.text import slugify

from users.models import User


UserModel = User


class Profile(models.Model):
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
    )

    slug = models.SlugField(max_length=100, null=True)
    avatar = models.URLField(max_length=100, null=True)
    cover_pic = models.URLField(max_length=500, null=True)
    description = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.user.username)  # type: ignore

        if self.avatar is None or "ui-avatars.com" in self.avatar:  # type: ignore
            username = f"{self.user.username}"  # type: ignore
            self.avatar = f"https://ui-avatars.com/api/?name={parse.quote(username)}"
        super().save(*args, **kwargs)
