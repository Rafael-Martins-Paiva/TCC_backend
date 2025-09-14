from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(recipient_email: str, verification_token: str):
    subject = "Verifique seu Email para o TCC_backend"

    base_url = getattr(settings, "BASE_VERIFICATION_URL", "http://localhost:8000")
    verification_url = f"{base_url}/api/v1/accounts/verify-email/?email={recipient_email}&token={verification_token}"

    message = (
        f"Olá!\n\nObrigado por se registrar no TCC_backend. "
        f"Por favor, clique no link abaixo para verificar seu email:\n\n"
        f"{verification_url}\n\nAtenciosamente,\nEquipe TCC_backend"
    )
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, "DEFAULT_FROM_EMAIL") else "noreply@tcc_backend.com"
    recipient_list = [recipient_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
