from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from developers.models import Developer, Subscription
from cards.models import Card

User = get_user_model()


class DeveloperAPITests(APITestCase):
    def setUp(self):
        # ✅ Создаём обычного пользователя
        self.user = User.objects.create_user(
            phone_number='89999999999',
            password='123456'
        )
        # ✅ Создаём суперпользователя
        self.superuser = User.objects.create_superuser(
            phone_number='80000000000',
            password='admin'
        )

        # ✅ Создаём застройщика
        self.developer = Developer.objects.create(
            name='Dream Builder',
            created_by=self.superuser
        )

        # ✅ Добавляем один ЖК
        self.card = Card.objects.create(
            title='ЖК Солнечный',
            address='г. Махачкала, ул. Центральная 10',
            description='Классный дом у моря',
            price=5000000,
            rooms=3,
            city=1,
            owner=self.superuser,
            developer=self.developer
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)  # Авторизуем пользователя

    def test_get_all_developers(self):
        url = reverse('developer_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Dream Builder')

    def test_get_cards_by_developer(self):
        url = reverse('developer_cards', args=[self.developer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'ЖК Солнечный')

    def test_subscribe_to_developer(self):
        url = reverse('subscribe', args=[self.developer.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(user=self.user, developer=self.developer).exists()
        )

    def test_unsubscribe_from_developer(self):
        Subscription.objects.create(user=self.user, developer=self.developer)
        url = reverse('unsubscribe', args=[self.developer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, developer=self.developer).exists()
        )

    def test_get_my_subscriptions(self):
        Subscription.objects.create(user=self.user, developer=self.developer)
        url = reverse('my_subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['developer']['name'], 'Dream Builder')

    def test_subscribe_twice_should_fail(self):
        Subscription.objects.create(user=self.user, developer=self.developer)
        url = reverse('subscribe', args=[self.developer.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_to_nonexistent_developer(self):
        url = reverse('subscribe', args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
