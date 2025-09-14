from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("name"), max_length=255, blank=True)
    bio = models.TextField(_("biography"), blank=True)
    USERNAME_FIELD = "email"
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    bio = models.TextField(max_length=500, blank=True)
    has_paid_plan = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)
