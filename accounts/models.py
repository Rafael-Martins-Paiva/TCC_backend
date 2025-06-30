from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    bio = models.TextField(_("biography"), blank=True)
    USERNAME_FIELD = 'email'
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, null=True, blank=True)
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    def __str__(self):
        return self.email
