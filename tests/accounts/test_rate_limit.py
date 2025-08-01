from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    },
    # Desabilitar o modo DEBUG para que o decorador @rate_limit seja ativado
    DEBUG=False
)
class RateLimitTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/accounts/google/login/"

    def test_google_login_rate_limit_exceeded(self):
        """
        Verifica se o rate limit bloqueia requisições após o limite ser excedido.
        """
        # As 10 primeiras chamadas devem ser permitidas (mesmo que resultem em erro 400 por falta de token)
        for _ in range(10):
            response = self.client.post(self.url, {})
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # A 11ª chamada deve ser bloqueada pelo rate limit
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("Retry-After", response.headers)

    def test_rate_limit_resets_after_window(self):
        """
        Verifica se o rate limit é resetado após a janela de tempo.
        Este teste ainda não é possível com a implementação atual, pois depende de 
        manipular o tempo, o que requer bibliotecas como `freezegun`.
        """
        pass
