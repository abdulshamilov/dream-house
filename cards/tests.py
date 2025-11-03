from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from cards.models import Card, CallRequest

User = get_user_model()


class CardTests(APITestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            phone_number="+79990000000",
            password="testpass123",
            name="TestUser"
        )
        self.client.force_authenticate(user=self.user)

        # Создаем карточку
        self.card = Card.objects.create(
            owner=self.user,
            title="Уютная квартира в центре",
            address="ул. Ленина, 1",
            description="Отличная квартира для семьи",
            price=5000000,
            rooms=2,
            city=1,  # ✅ теперь число (ID города из CITY_CHOICES)
            house_type="apartment",
            building_material="brick",
            category="flat",
            floors_total=5,
            elevator="passenger",
            parking="none",
            balcony=True,
            ceiling_height=2.8,
            area=60.5,
            latitude=42.98,
            longitude=47.51,
        )

    def test_get_cards_list(self):
        url = reverse("cards_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Уютная квартира в центре")

    def test_get_card_detail(self):
        url = reverse("card_detail", args=[self.card.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.card.title)

    def test_filter_cards_by_city(self):
        url = reverse("cards_list")
        response = self.client.get(url, {"city": 1})  # ✅ передаём число, не строку
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(str(card["city"]) == "1" for card in response.data))

    def test_rate_card(self):
        url = reverse("card_rate", args=[self.card.id])
        data = {"rating": 5}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("new_average", response.data)
        self.card.refresh_from_db()
        self.assertEqual(round(self.card.rating, 2), 5.00)
        self.assertEqual(self.card.rating_count, 1)

    def test_unauthenticated_cannot_rate(self):
        self.client.logout()
        url = reverse("card_rate", args=[self.card.id])
        data = {"rating": 4}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_call_request(self):
        url = reverse("call_request", args=[self.card.id])
        data = {
            "phone_number": "+79998887766",
            "name": "Ахмад",
            "preferred_time": "После 18:00"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CallRequest.objects.filter(phone_number="+79998887766").exists())

    def test_call_request_missing_fields(self):
        url = reverse("call_request", args=[self.card.id])
        data = {"phone_number": ""}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
