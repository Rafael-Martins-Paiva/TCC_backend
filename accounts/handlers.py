from accounts.email_utils import send_verification_email
from domain.accounts.events.user_registered import UserRegistered


def send_verification_email_on_user_registered(event: UserRegistered):
    send_verification_email(event.email, event.verification_token)
