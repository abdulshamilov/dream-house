from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+79990001122",
            password="testpassword123",
            name="Test"
        )

    def test_register_user(self):
        url = reverse('register')
        data = {
            "phone_number": "+79990002233",
            "name": "New",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['ok'])
        self.assertEqual(response.data['code'], 'OK')
        self.assertTrue(User.objects.filter(phone_number="+79990002233").exists())

    def test_register_missing_password(self):
        url = reverse('register')
        data = {
            "phone_number": "+79990003344",
            "name": "NoPassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['ok'])
        self.assertEqual(response.data['reason'], 'MISSING_PASSWORD')

    def test_register_missing_name(self):
        url = reverse('register')
        data = {
            "phone_number": "+79990004455",
            "password": "test123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['ok'])
        self.assertEqual(response.data['reason'], 'MISSING_NAME')

    def test_register_already_exists(self):
        url = reverse('register')
        data = {
            "phone_number": "+79990001122",
            "name": "Test",
            "password": "any"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['ok'])
        self.assertEqual(response.data['reason'], 'ALREADY_REGISTERED')
        self.assertEqual(response.data['code'], 'REGIST_FAILED')

    def test_login_user(self):
        url = reverse('token_obtain_pair')
        data = {
            "phone_number": "+79990001122",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_me_authenticated(self):
        # Получаем токен
        url_token = reverse('token_obtain_pair')
        response = self.client.post(
            url_token,
            {"phone_number": "+79990001122", "password": "testpassword123"},
            format='json'
        )
        access_token = response.data['access']

        # Проверяем endpoint /me/
        url_me = reverse('me')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url_me)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ok'])
        self.assertEqual(response.data['code'], 'OK')
        self.assertEqual(response.data['user']['phone_number'], "+79990001122")

    def test_get_me_unauthenticated(self):
        url_me = reverse('me')
        response = self.client.get(url_me)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # Users List
    # --------------------
    def test_get_all_users_authenticated(self):
        url_token = reverse('token_obtain_pair')
        response = self.client.post(
            url_token,
            {"phone_number": "+79990001122", "password": "testpassword123"},
            format='json'
        )
        access_token = response.data['access']

        url_users = reverse('users-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url_users)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[0]['phone_number'], "+79990001122")

    def test_get_all_users_unauthenticated(self):
        url_users = reverse('users-list')
        response = self.client.get(url_users)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
