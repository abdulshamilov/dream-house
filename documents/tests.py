from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from cards.models import Card
from .models import Document
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class DocumentTests(APITestCase):

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
            title="Тестовая квартира",
            address="ул. Ленина, 1",
            description="Тестовая",
            price=1000000,
            rooms=2,
            city="1",
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

        # Подготовка тестового файла PDF
        self.pdf_file = SimpleUploadedFile("test.pdf", b"%PDF-1.4 test content", content_type="application/pdf")

    def test_add_document(self):
        url = reverse("document_add", args=[self.card.id])
        data = {
            "card": self.card.id,
            "title": "Документ 1",
            "file": self.pdf_file
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Document.objects.filter(card=self.card).exists())

    def test_limit_documents(self):
        url = reverse("document_add", args=[self.card.id])
        # Добавляем 5 документов
        for i in range(5):
            file = SimpleUploadedFile(f"test{i}.pdf", b"%PDF-1.4 test content", content_type="application/pdf")
            data = {"card": self.card.id, "title": f"Документ {i+1}", "file": file}
            response = self.client.post(url, data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Попытка добавить 6-й документ
        file6 = SimpleUploadedFile("test6.pdf", b"%PDF-1.4 test content", content_type="application/pdf")
        data6 = {"card": self.card.id, "title": "Документ 6", "file": file6}
        response6 = self.client.post(url, data6, format="multipart")
        self.assertEqual(response6.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Нельзя добавить больше 5 документов", str(response6.data))

    def test_get_documents_list(self):
        # Добавляем 2 документа
        for i in range(2):
            Document.objects.create(card=self.card, title=f"Документ {i+1}", file=self.pdf_file)

        url = reverse("documents_list", args=[self.card.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Документ 1")
