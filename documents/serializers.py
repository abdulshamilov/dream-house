from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'card', 'title', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']


    def validate(self, data):
        card = data.get('card')
        if card.documents.count() >= 5:
            raise serializers.ValidationError("Нельзя добавить больше 5 документов к одной карточке")
        return data
