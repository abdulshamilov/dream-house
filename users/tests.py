from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
            name="Test"
        )

    def test_register_user(self):
        url = reverse('register')
        data = {
            "email": "newuser@example.com",
            "name": "New",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['ok'])
        self.assertEqual(response.data['code'], 'OK')
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_already_exists(self):
        url = reverse('register')
        data = {
            "email": "test@example.com",
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
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_me_authenticated(self):
        url_token = reverse('token_obtain_pair')
        response = self.client.post(
            url_token,
            {"email": "test@example.com", "password": "testpassword123"},
            format='json'
        )
        access_token = response.data['access']

        url_me = reverse('me')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url_me)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ok'])
        self.assertEqual(response.data['code'], 'OK')
        self.assertEqual(response.data['user']['email'], "test@example.com")

    def test_get_me_unauthenticated(self):
        url_me = reverse('me')
        response = self.client.get(url_me)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# --------------------
# Тест для UsersListView
# --------------------
    def test_get_all_users_authenticated(self):
        url_token = reverse('token_obtain_pair')
        response = self.client.post(
            url_token,
            {"email": "test@example.com", "password": "testpassword123"},
            format='json'
        )
        access_token = response.data['access']

        url_users = reverse('users-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url_users)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)  # хотя бы один пользователь есть
        self.assertEqual(response.data[0]['email'], "test@example.com")

    def test_get_all_users_unauthenticated(self):
        url_users = reverse('users-list')
        response = self.client.get(url_users)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
