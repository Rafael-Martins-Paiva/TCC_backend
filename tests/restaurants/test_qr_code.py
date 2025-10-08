from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
import uuid

from restaurants.models import Restaurant
from core.qr_codes import QRCodeGenerator
from restaurants.domain.services import RestaurantURLService
from restaurants.services import GenerateRestaurantQRCodeUseCase

User = get_user_model()

class QRCodeGeneratorTests(TestCase):
    def test_generate_qr_code(self):
        generator = QRCodeGenerator()
        data = "http://testserver/some-restaurant/"
        qr_code_bytes = generator.generate(data)
        self.assertIsInstance(qr_code_bytes, bytes)
        self.assertGreater(len(qr_code_bytes), 0)

class RestaurantURLServiceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.user)

    def test_get_public_url(self):
        service = RestaurantURLService()
        # Mock a request to get a base_url
        mock_request = self.factory.get('/')
        mock_request.META = {'HTTP_HOST': 'testserver'}
        base_url = mock_request.build_absolute_uri('/')

        expected_path = reverse('web:restaurant_detail', kwargs={'pk': self.restaurant.pk})
        expected_url = f"http://testserver{expected_path}"
        
        generated_url = service.get_public_url(self.restaurant.pk, base_url)
        self.assertEqual(generated_url, expected_url)

class GenerateRestaurantQRCodeUseCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.user)
        self.mock_url_service = MagicMock(spec=RestaurantURLService)
        self.mock_qr_generator = MagicMock(spec=QRCodeGenerator)
        self.use_case = GenerateRestaurantQRCodeUseCase(self.mock_url_service, self.mock_qr_generator)

    def test_execute(self):
        mock_base_url = "http://testserver/"
        mock_restaurant_url = "http://testserver/restaurants/" + str(self.restaurant.pk) + "/"
        mock_qr_bytes = b"mock_qr_code_bytes"

        self.mock_url_service.get_public_url.return_value = mock_restaurant_url
        self.mock_qr_generator.generate.return_value = mock_qr_bytes

        result_bytes = self.use_case.execute(self.restaurant.pk, mock_base_url)

        self.assertEqual(result_bytes, mock_qr_bytes)
        self.mock_url_service.get_public_url.assert_called_once_with(self.restaurant.pk, mock_base_url)
        self.mock_qr_generator.generate.assert_called_once_with(mock_restaurant_url)

class RestaurantQRCodeAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='owner', email='owner@example.com', password='password')
        self.non_owner = User.objects.create_user(email='nonowner@example.com', password='password', name='nonowner')
        self.restaurant = Restaurant.objects.create(name='Owner Restaurant', owner=self.user)
        self.url = reverse('restaurant-qr-code', kwargs={'pk': self.restaurant.pk})

    def test_generate_qr_code_by_owner(self):
        self.client.login(username='owner', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertGreater(len(response.content), 0)

    def test_generate_qr_code_by_non_owner(self):
        self.client.login(username='nonowner', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_generate_qr_code_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401) # Unauthorized

    def test_generate_qr_code_for_nonexistent_restaurant(self):
        self.client.login(username='owner', password='password')
        non_existent_uuid = uuid.uuid4()
        url = reverse('restaurant-qr-code', kwargs={'pk': non_existent_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) # Not Found
