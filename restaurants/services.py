import bleach
from django.contrib.auth import get_user_model
import uuid

from core.qr_codes import QRCodeGenerator
from restaurants.domain.services import RestaurantURLService

# import re # No longer needed for script tag removal
from .models import Restaurant

User = get_user_model()


class CreateRestaurantService:
    def execute(self, name: str, owner: User) -> Restaurant:
        restaurant = Restaurant.objects.create(name=name, owner=owner)
        return restaurant


class UpdateRestaurantContentService:
    # WARNING: Allowing script tags and style attributes directly opens up significant XSS vulnerabilities.
    # This is done as per user request, but is NOT recommended for production environments without
    # further, more robust sandboxing (e.g., iframes with strict sandbox attributes) or a very
    # sophisticated HTML/CSS/JS sanitizer.
    ALLOWED_TAGS = [
        "p",
        "strong",
        "em",
        "u",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "br",
        "img",
        "a",
        "ul",
        "ol",
        "li",
        "blockquote",
        "code",
        "pre",
        "script",
        "style",  # Added script and style tags as per user request
    ]
    ALLOWED_ATTRIBUTES = {
        "*": ["class", "style"],  # Added style attribute for all tags
        "a": ["href", "title"],
        "img": ["src", "alt"],
    }

    def execute(self, restaurant: Restaurant, html_content: str) -> Restaurant:
        # As per user request, script tags are now allowed and will be processed by bleach.
        # However, bleach's default behavior for script tags is to remove them unless explicitly allowed.
        # By adding 'script' to ALLOWED_TAGS, bleach will now keep them.
        # For CSS, bleach does not sanitize 'style' attributes by default.
        # To properly sanitize CSS, a css_sanitizer would be required.
        # This implementation allows raw CSS and JS as per user's explicit instruction,
        # but it's a significant security risk.

        sanitized_content = bleach.clean(
            html_content,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=False,  # Set to False to keep content inside tags like script
        )
        restaurant.website_content = sanitized_content
        restaurant.save()
        return restaurant


class GenerateRestaurantQRCodeUseCase:
    def __init__(self, url_service: RestaurantURLService, qr_generator: QRCodeGenerator):
        self.url_service = url_service
        self.qr_generator = qr_generator

    def execute(self, restaurant_id: uuid.UUID, base_url: str) -> bytes:
        restaurant_url = self.url_service.get_public_url(restaurant_id, base_url)
        qr_code_image_bytes = self.qr_generator.generate(restaurant_url)
        return qr_code_image_bytes