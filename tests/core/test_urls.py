from django.test import SimpleTestCase
from django.urls import resolve, reverse
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import CustomTokenObtainPairView
from users.views import UserMeView


class UrlsTest(SimpleTestCase):

    def test_admin_url_resolves(self):
        url = reverse("admin:index")
        self.assertEqual(resolve(url).func.__module__, "django.contrib.admin.sites")

    def test_user_me_url_resolves(self):
        url = reverse("user-me")
        self.assertEqual(resolve(url).func.view_class, UserMeView)

    def test_token_obtain_pair_url_resolves(self):
        url = reverse("token_obtain_pair")
        self.assertEqual(resolve(url).func.view_class, CustomTokenObtainPairView)

    def test_token_refresh_url_resolves(self):
        url = reverse("token_refresh")
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)
