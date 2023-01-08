from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, default='-инкогнито-')
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    password = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_admin = True
        if self.is_admin:
            self.is_staff = True
        return super().save(*args, **kwargs)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe',
            )
        ]

    def __str__(self):
        return f'{self.user} follows {self.author}'
