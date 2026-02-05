import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from cards.models import Card
from notifications.models import Notification


class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            phone_number="+70000000000",
            password="password123",
        )
        self.temp_media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_media)

    def _create_card(self, price=4500000, owner=None):
        return Card.objects.create(
            owner=owner or self.user,
            title="Квартира",
            address="Адрес",
            description="Описание",
            price=Decimal(str(price)),
        )

    def test_list_returns_image_and_prices(self):
        with override_settings(MEDIA_ROOT=self.temp_media):
            card = self._create_card(price=4500000)
            card.images.create(
                image=SimpleUploadedFile(
                    "photo.jpg",
                    b"fake image bytes",
                    content_type="image/jpeg",
                )
            )

            Notification.objects.create(
                user=self.user,
                card=card,
                old_price=Decimal("5300000"),
                type=Notification.TYPE_PRICE_DROP,
                title="Цена снижена",
                message="Теперь дешевле",
            )

            self.client.force_authenticate(user=self.user)
            response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]

        self.assertEqual(result["card_id"], str(card.id))
        self.assertEqual(result["price"], 4500000)
        self.assertEqual(result["old_price"], 5300000)
        self.assertTrue(result["image_url"].startswith("http://testserver"))
        self.assertTrue(result["image_url"].endswith("photo.jpg"))
        self.assertEqual(result["type"], Notification.TYPE_PRICE_DROP)

    def test_old_price_returned_as_is(self):
        """old_price возвращается как есть (логика сравнения на фронте)"""
        card = self._create_card(price=6200000)
        Notification.objects.create(
            user=self.user,
            card=card,
            old_price=Decimal("6000000"),  # меньше текущей цены
            type=Notification.TYPE_SUBSCRIPTION,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result["price"], 6200000)
        # old_price теперь возвращается как есть
        self.assertEqual(result["old_price"], 6000000)

    def test_fields_null_when_no_card(self):
        Notification.objects.create(
            user=self.user,
            title="Системное",
            message="Сообщение",
            type=Notification.TYPE_SYSTEM,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertIsNone(result["card_id"])
        self.assertIsNone(result["image_url"])
        self.assertIsNone(result["price"])
        self.assertIsNone(result["old_price"])

    def test_image_url_none_when_no_images(self):
        card = self._create_card(price=5100000)
        Notification.objects.create(
            user=self.user,
            card=card,
            type=Notification.TYPE_NEW,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result["price"], 5100000)
        self.assertIsNone(result["image_url"])

    def test_price_rounds_half_up(self):
        card = self._create_card(price=Decimal("1234567.50"))
        Notification.objects.create(user=self.user, card=card)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        # 1234567.50 -> 1234568 (ROUND_HALF_UP)
        self.assertEqual(result["price"], 1234568)

    def test_notifications_are_user_scoped(self):
        other_user = get_user_model().objects.create_user(
            phone_number="+71111111111", password="password123"
        )
        Notification.objects.create(user=other_user)
        Notification.objects.create(user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_ordering_by_created_desc(self):
        first = Notification.objects.create(user=self.user, title="old")
        second = Notification.objects.create(user=self.user, title="new")

        # move timestamps to enforce ordering: second newer
        Notification.objects.filter(id=first.id).update(created_at="2024-01-01T00:00:00Z")
        Notification.objects.filter(id=second.id).update(created_at="2024-01-02T00:00:00Z")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertEqual(titles[0], "new")
        self.assertEqual(titles[1], "old")

    def test_mark_read_only_for_owner(self):
        notif = Notification.objects.create(user=self.user, is_read=False)
        url = reverse("notification_read", args=[notif.id])

        # Owner can mark read
        self.client.force_authenticate(user=self.user)
        res_owner = self.client.patch(url, {})
        self.assertEqual(res_owner.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

        # Other user gets 404 due to queryset restriction
        other = get_user_model().objects.create_user(
            phone_number="+72222222222", password="password123"
        )
        self.client.force_authenticate(user=other)
        res_other = self.client.patch(url, {})
        self.assertEqual(res_other.status_code, status.HTTP_404_NOT_FOUND)


class NotificationSignalTests(TestCase):
    """Тесты сигналов создания уведомлений"""

    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            phone_number="+70000000001", password="password123"
        )
        self.subscriber = get_user_model().objects.create_user(
            phone_number="+70000000002", password="password123"
        )

    def test_new_card_creates_notification_with_card_link(self):
        """При создании карточки подписчик получает уведомление с привязкой к карточке"""
        from developers.models import Developer, Subscription

        developer = Developer.objects.create(name="Test Dev")
        Subscription.objects.create(user=self.subscriber, developer=developer)

        # Создаём карточку — должен сработать сигнал
        card = Card.objects.create(
            owner=self.owner,
            developer=developer,
            title="Новая квартира",
            address="ул. Тестовая",
            description="Описание",
            price=Decimal("4000000"),
            rooms=2,
            area=Decimal("50"),
        )

        # Проверяем уведомление
        notification = Notification.objects.filter(user=self.subscriber).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.card, card)  # Привязка к карточке!
        self.assertEqual(notification.type, Notification.TYPE_SUBSCRIPTION)
        self.assertIn("застройщика", notification.title)

    def test_notification_serializer_returns_price_from_linked_card(self):
        """Сериализатор возвращает price из привязанной карточки"""
        from developers.models import Developer, Subscription
        from notifications.serializers import NotificationSerializer

        developer = Developer.objects.create(name="Dev")
        Subscription.objects.create(user=self.subscriber, developer=developer)

        card = Card.objects.create(
            owner=self.owner,
            developer=developer,
            title="Квартира с ценой",
            address="Адрес",
            description="Описание",
            price=Decimal("3500000"),
            rooms=1,
            area=Decimal("35"),
        )

        notification = Notification.objects.filter(user=self.subscriber).first()
        serializer = NotificationSerializer(notification)
        data = serializer.data

        self.assertEqual(data["price"], 3500000)
        self.assertEqual(data["card_id"], str(card.id))

