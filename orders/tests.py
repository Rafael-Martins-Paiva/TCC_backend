from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, MenuItem
from accounts.models import UserRole
from orders.models import Order, OrderItem
import decimal

User = get_user_model()

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com', password='password123', name='User One')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password123', name='User Two')
        self.restaurant_owner = User.objects.create_user(email='owner1@example.com', password='password123', name='Restaurant Owner', role=UserRole.RESTAURANT_OWNER)

        self.restaurant1 = Restaurant.objects.create(
            name='Restaurant One',
            owner=self.restaurant_owner
        )
        self.menu_item1 = MenuItem.objects.create(
            restaurant=self.restaurant1,
            name='Burger',
            description='Classic Burger',
            price=decimal.Decimal('10.00')
        )
        self.menu_item2 = MenuItem.objects.create(
            restaurant=self.restaurant1,
            name='Fries',
            description='Crispy Fries',
            price=decimal.Decimal('3.50')
        )

        self.restaurant2 = Restaurant.objects.create(
            name='Restaurant Two',
            owner=self.user2 # user2 is owner of restaurant2
        )
        self.menu_item3 = MenuItem.objects.create(
            restaurant=self.restaurant2,
            name='Pizza',
            description='Pepperoni Pizza',
            price=decimal.Decimal('15.00')
        )

        self.order_data = {
            'restaurant': self.restaurant1.id,
            'items': [
                {'menu_item': self.menu_item1.id, 'quantity': 2},
                {'menu_item': self.menu_item2.id, 'quantity': 1},
            ]
        }

        # Create an order for user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('order-list-create'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.order1 = Order.objects.get(id=response.data['id'])
        self.client.force_authenticate(user=None) # Clear authentication

    def test_create_order_authenticated(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(reverse('order-list-create'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2) # user1's order + user2's order
        self.assertEqual(response.data['user'], self.user2.email)
        self.assertEqual(response.data['restaurant'], self.restaurant1.id)
        self.assertEqual(response.data['total_price'], '23.50') # 2*10.00 + 1*3.50

    def test_create_order_unauthenticated(self):
        response = self.client.post(reverse('order-list-create'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_invalid_menu_item_for_restaurant(self):
        invalid_order_data = {
            'restaurant': self.restaurant1.id,
            'items': [
                {'menu_item': self.menu_item3.id, 'quantity': 1}, # menu_item3 belongs to restaurant2
            ]
        }
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('order-list-create'), invalid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Menu item', str(response.data[0]))

    def test_list_orders_as_order_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('order-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.order1.id))

    def test_list_orders_as_restaurant_owner(self):
        self.client.force_authenticate(user=self.restaurant_owner)
        response = self.client.get(reverse('order-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.order1.id))

    def test_list_orders_as_other_user(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('order-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # user2 has no orders and doesn't own restaurant1

    def test_retrieve_order_as_order_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.order1.id))

    def test_retrieve_order_as_restaurant_owner(self):
        self.client.force_authenticate(user=self.restaurant_owner)
        response = self.client.get(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.order1.id))

    def test_retrieve_order_as_other_user_forbidden(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_status_as_restaurant_owner(self):
        self.client.force_authenticate(user=self.restaurant_owner)
        update_data = {'status': 'preparing'}
        response = self.client.patch(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'preparing')

    def test_update_order_status_as_order_owner_forbidden(self):
        self.client.force_authenticate(user=self.user1)
        update_data = {'status': 'completed'}
        response = self.client.patch(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_status_as_other_user_forbidden(self):
        self.client.force_authenticate(user=self.user2)
        update_data = {'status': 'completed'}
        response = self.client.patch(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_pending_order_as_order_owner(self):
        # Ensure order1 is pending
        self.order1.status = 'pending'
        self.order1.save()

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_non_pending_order_forbidden(self):
        self.order1.status = 'preparing'
        self.order1.save()

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only pending orders can be cancelled by the order owner, or any order by an admin.', response.data['detail'])
        self.assertEqual(Order.objects.count(), 1)

    def test_delete_order_as_restaurant_owner_forbidden(self):
        self.client.force_authenticate(user=self.restaurant_owner)
        response = self.client.delete(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only pending orders can be cancelled by the order owner, or any order by an admin.', response.data['detail'])
        self.assertEqual(Order.objects.count(), 1)

    def test_delete_order_as_other_user_forbidden(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(reverse('order-retrieve-update-destroy', kwargs={'id': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have permission to perform this action.', response.data['detail'])
        self.assertEqual(Order.objects.count(), 1)
