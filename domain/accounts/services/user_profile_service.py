from ..repositories.account_repository import AbstractUserRepository


class UserProfileService:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo

    def update_profile(self, user_id: int, update_data: dict):
        user_entity = self.user_repo.get_by_id(user_id)

        if "bio" in update_data:
            user_entity.set_bio(update_data["bio"])
            del update_data["bio"]

        if "name" in update_data:
            user_entity.name = update_data["name"]
            del update_data["name"]

        if "username" in update_data:
            raise ValueError("Não é permitido alterar o nome de usuário por esta rota.")

        for key, value in update_data.items():
            setattr(user_entity, key, value)

        self.user_repo.update(user_entity)
