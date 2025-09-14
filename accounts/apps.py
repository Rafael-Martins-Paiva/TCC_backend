from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from domain.accounts.events.user_registered import UserRegistered
        from domain.events.dispatcher import dispatcher

        from .handlers import send_verification_email_on_user_registered

        dispatcher.register(UserRegistered, send_verification_email_on_user_registered)
