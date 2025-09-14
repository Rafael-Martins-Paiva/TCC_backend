from uuid import UUID

from django.contrib.auth import get_user_model

User = get_user_model()


class Restaurant:
    def __init__(self, id: UUID, name: str, owner: User, website_content: str = ""):
        self.id = id
        self.name = name
        self.owner = owner
        self.website_content = website_content
