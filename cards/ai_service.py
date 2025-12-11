"""
AI Service для работы с Claude/GPT API
Интегрируется с базой данных карточек недвижимости
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from django.db.models import Q

logger = logging.getLogger(__name__)


class AIAssistantService:
    """Сервис для работы с AI ассистентом"""

    def __init__(self):
        from .models import AIAssistant, Card
        self.AIAssistant = AIAssistant
        self.Card = Card
        self.config = self._load_config()
        self.client = self._init_client()

    def _load_config(self):
        """Загрузить конфигурацию AI ассистента"""
        try:
            config = self.AIAssistant.objects.filter(is_active=True).first()
            if not config:
                logger.warning("AI Assistant is not configured")
                return None
            return config
        except Exception as e:
            logger.error(f"Failed to load AI config: {e}")
            return None

    def _init_client(self):
        """Инициализировать клиент API в зависимости от провайдера"""
        if not self.config or self.config.api_provider == 'disabled':
            return None

        api_key = self.config.get_api_key()
        if not api_key:
            logger.error(f"{self.config.api_provider.title()} API key not found")
            return None

        try:
            if self.config.api_provider == 'openai':
                from openai import OpenAI
                return OpenAI(api_key=api_key)
            elif self.config.api_provider == 'anthropic':
                import anthropic
                return anthropic.Anthropic(api_key=api_key)
        except ImportError as e:
            logger.error(f"{self.config.api_provider.title()} library not installed: {e}")
            return None

        return None

    def search_cards(self, query: str, preferences: Optional[Dict] = None, limit: int = 5) -> List[Dict]:
        """
        Поиск карточек по поисковому запросу и предпочтениям
        
        Args:
            query: Текстовый поисковый запрос
            preferences: Словарь с предпочтениями (city, price_min, price_max, rooms и т.д.)
            limit: Максимальное количество результатов
        
        Returns:
            Список карточек с информацией
        """
        queryset = self.Card.objects.all()
        
        # Полнотекстовый поиск
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
        
        # Применить предпочтения пользователя
        if preferences:
            filter_map = {
                'city': 'city',
                'rooms': 'rooms',
                'house_type': 'house_type',
                'price_min': 'price__gte',
                'price_max': 'price__lte',
            }
            
            for pref_key, filter_key in filter_map.items():
                if pref_key in preferences and preferences[pref_key] is not None:
                    queryset = queryset.filter(**{filter_key: preferences[pref_key]})
        
        return [self._format_card(card) for card in queryset[:limit]]

    def _format_card(self, card) -> Dict:
        """Форматировать карточку для передачи в AI"""
        return {
            'id': card.id,
            'title': card.title,
            'address': card.address,
            'price': float(card.price),
            'rooms': card.rooms,
            'area': float(card.area),
            'city': card.get_city_display() if hasattr(card, 'get_city_display') else str(card.city),
            'house_type': card.get_house_type_display() if hasattr(card, 'get_house_type_display') else card.house_type,
            'description': card.description[:200],  # Краткое описание
            'rating': float(card.rating),
            'elevator': card.get_elevator_display() if hasattr(card, 'get_elevator_display') else card.elevator,
            'parking': card.get_parking_display() if hasattr(card, 'get_parking_display') else card.parking,
        }

    def chat(self, user_message: str, user_preferences: Optional[Dict] = None, user_id: Optional[int] = None) -> Dict:
        """
        Отправить сообщение AI и получить ответ
        
        Args:
            user_message: Сообщение от пользователя
            user_preferences: Предпочтения пользователя
            user_id: ID пользователя для сохранения истории
        
        Returns:
            Словарь с ответом и информацией
        """
        if not self.client or not self.config:
            return {
                'error': 'AI Assistant is not configured',
                'response': 'К сожалению, AI ассистент не настроен. Пожалуйста, обратитесь к администратору.'
            }

        try:
            # Поиск релевантных карточек
            search_results = self.search_cards(user_message, user_preferences)
            
            # Построить контекст для AI
            context = self._build_context(user_message, search_results, user_preferences)
            
            # Отправить запрос к API
            response_data = self._call_api(context)
            
            if response_data['success']:
                # Сохранить в историю если user_id предоставлен
                if user_id:
                    self._save_to_history(
                        user_id,
                        user_message,
                        response_data['response'],
                        search_results,
                        response_data.get('tokens_used', 0)
                    )
                
                return {
                    'success': True,
                    'response': response_data['response'],
                    'tokens_used': response_data.get('tokens_used', 0),
                    'referenced_cards': [card['id'] for card in search_results]
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('error', 'Unknown error'),
                    'response': 'Произошла ошибка при обработке вашего запроса.'
                }

        except Exception as e:
            logger.exception(f"AI Chat error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Произошла ошибка при обработке вашего запроса.'
            }

    def _build_context(self, user_message: str, search_results: List[Dict], preferences: Optional[Dict]) -> str:
        """Построить контекст для отправки в API"""
        context = f"""Пользователь ищет недвижимость с параметрами: {json.dumps(preferences, ensure_ascii=False, indent=2)}

Найденные карточки из базы данных:
"""
        for i, card in enumerate(search_results, 1):
            context += f"\n{i}. {card['title']} ({card['address']}) - {card['price']}₽, {card['rooms']} комнат"
        
        context += f"\n\nПросьба пользователя: {user_message}"
        
        return context

    def _call_api(self, context: str) -> Dict:
        """Отправить запрос к API провайдера"""
        api_methods = {
            'openai': self._call_openai,
            'anthropic': self._call_anthropic,
        }
        
        api_method = api_methods.get(self.config.api_provider)
        if not api_method:
            return {'success': False, 'error': f'Unknown API provider: {self.config.api_provider}'}
        
        return api_method(context)

    def _call_openai(self, context: str) -> Dict:
        """Вызвать OpenAI API"""
        try:
            message = self.client.chat.completions.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": context}
                ]
            )

            return {
                'success': True,
                'response': message.choices[0].message.content,
                'tokens_used': message.usage.total_tokens
            }

        except Exception as e:
            logger.exception(f"OpenAI API error: {e}")
            return {'success': False, 'error': str(e)}

    def _call_anthropic(self, context: str) -> Dict:
        """Вызвать Anthropic Claude API"""
        try:
            message = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                system=self.config.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=self.config.temperature,
            )

            response_text = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens

            return {
                'success': True,
                'response': response_text,
                'tokens_used': tokens_used
            }

        except Exception as e:
            logger.exception(f"Claude API call error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _save_to_history(self, user_id: int, message: str, response: str, cards: List[Dict], tokens: int):
        """Сохранить чат в историю"""
        try:
            from .models import ChatMessage
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            chat = ChatMessage.objects.create(
                user=user,
                message=message,
                response=response,
                tokens_used=tokens
            )
            
            # Добавить связанные карточки
            if cards:
                card_ids = [card['id'] for card in cards]
                chat.referenced_cards.set(self.Card.objects.filter(id__in=card_ids), clear=True)
            
            return chat

        except Exception as e:
            logger.exception(f"Failed to save chat history: {e}")
            return None
