from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from restaurants.models import Restaurant

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a test restaurant for demonstration purposes."

    def handle(self, *args, **options):
        # Create a test user or get an existing one
        user, created = User.objects.get_or_create(
            email="testowner@example.com",
        )
        if created:
            user.set_password("testpassword")
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully created test user "testowner@example.com"'))

        # Create a test restaurant
        restaurant_name = "pizzaria"
        restaurant, created = Restaurant.objects.get_or_create(
            name=restaurant_name,
            owner=user,
            defaults={"website_content": "<h1>Bem-vindo à Pizzaria de Teste!</h1><p>Este é um site de teste.</p>"},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created test restaurant "{restaurant_name}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Restaurant "{restaurant_name}" already exists.'))
