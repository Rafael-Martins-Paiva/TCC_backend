from django.test import TestCase

from accounts.models import User


class UserModelTest(TestCase):
    def test_is_admin_sets_is_staff_and_is_superuser(self):
        user = User.objects.create_user(email="test@example.com", password="password123")
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        user.is_admin = True
        user.save()

        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_is_admin_false_does_not_set_is_staff_and_is_superuser(self):
        user = User.objects.create_user(email="another@example.com", password="password123")
        user.is_admin = False
        user.save()

        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
