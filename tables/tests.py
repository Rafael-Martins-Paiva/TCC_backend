from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from restaurants.models import Restaurant
from accounts.models import User
from .models import Table


class TableAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.client.force_authenticate(user=self.user)
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.user)
        self.table_data = {
            'restaurant': self.restaurant,
            'table_number': 'T1',
            'capacity': 4,
            'status': 'available'
        }
        self.table = Table.objects.create(**self.table_data)

    def test_create_table(self):
        new_table_data = {
            'restaurant': self.restaurant.id,
            'table_number': 'T2',
            'capacity': 2,
            'status': 'occupied'
        }
        response = self.client.post(reverse('table-list'), new_table_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Table.objects.count(), 2)

    def test_list_tables(self):
        response = self.client.get(reverse('table-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Only tables for the authenticated user's restaurant

    def test_retrieve_table(self):
        response = self.client.get(reverse('table-detail', kwargs={'pk': self.table.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['table_number'], 'T1')

    def test_update_table(self):
        updated_data = {'capacity': 6, 'status': 'reserved'}
        response = self.client.patch(reverse('table-detail', kwargs={'pk': self.table.id}), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.table.refresh_from_db()
        self.assertEqual(self.table.capacity, 6)
        self.assertEqual(self.table.status, 'reserved')

    def test_set_table_status(self):
        response = self.client.patch(reverse('table-set-status', kwargs={'pk': self.table.id}), {'status': 'needs_cleaning'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.table.refresh_from_db()
        self.assertEqual(self.table.status, 'needs_cleaning')

    def test_delete_table(self):
        response = self.client.delete(reverse('table-detail', kwargs={'pk': self.table.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Table.objects.count(), 0)