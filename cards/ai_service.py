"""
AI Service для работы с OpenAI, Anthropic и DeepSeek API
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
            elif self.config.api_provider == 'deepseek':
                from openai import OpenAI
                # DeepSeek использует OpenAI-совместимый API
                return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
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
        
        # Полнотекстовый поиск по ключевым словам
        if query and query.strip():
            # Разделить запрос на ключевые слова
            keywords = query.lower().split()
            q_objects = Q()
            
            for keyword in keywords:
                q_objects |= (
                    Q(title__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(address__icontains=keyword) |
                    Q(city__in=self._parse_city_from_query(keyword))
                )
            
            queryset = queryset.filter(q_objects)
        
        # Применить предпочтения пользователя (фильтрация)
        if preferences and isinstance(preferences, dict):
            filter_map = {
                'city': 'city',
                'rooms': 'rooms',
                'house_type': 'house_type',
                'price_min': 'price__gte',
                'price_max': 'price__lte',
            }
            
            for pref_key, filter_key in filter_map.items():
                if pref_key in preferences and preferences[pref_key] is not None:
                    try:
                        queryset = queryset.filter(**{filter_key: preferences[pref_key]})
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid filter value for {pref_key}: {e}")
        
        # Сортировка по релевантности (рейтинг и свежесть)
        queryset = queryset.order_by('-rating', '-created_at')
        
        return [self._format_card(card) for card in queryset[:limit]]

    def _parse_city_from_query(self, keyword: str) -> List[int]:
        """Парсить название города из ключевого слова"""
        city_map = {
            'махачкала': 1,
            'махачкале': 1,
            'каспийск': 2,
            'каспийске': 2,
            'дербент': 3,
            'дербенте': 3,
        }
        return [city_map.get(keyword, None)] if keyword in city_map else []

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

    def chat(self, user_message: str, user_preferences: Optional[Dict] = None, user_id: Optional[int] = None, mode: str = 'search') -> Dict:
        """
        Отправить сообщение AI и получить ответ
        
        Args:
            user_message: Сообщение от пользователя
            user_preferences: Предпочтения пользователя для режима поиска
            user_id: ID пользователя для сохранения истории
            mode: 'search' - поиск квартир, 'free' - обычный чат без поиска
        
        Returns:
            Словарь с ответом и информацией
        """
        # Валидация клиента и конфигурации
        if not self.client or not self.config:
            logger.warning("AI Assistant not configured or client initialization failed")
            return {
                'success': False,
                'error': 'AI Assistant is not configured',
                'response': 'К сожалению, AI ассистент не настроен. Пожалуйста, обратитесь к администратору.'
            }

        # Валидация сообщения пользователя
        if not user_message or not isinstance(user_message, str) or not user_message.strip():
            return {
                'success': False,
                'error': 'Empty message',
                'response': 'Пожалуйста, отправьте сообщение.'
            }

        try:
            search_results = []
            context = user_message.strip()
            
            # Режим поиска квартир - ищет в БД и строит контекст с результатами
            if mode == 'search':
                search_results = self.search_cards(user_message, user_preferences, limit=5)
                context = self._build_context(user_message, search_results, user_preferences)
            
            # Режим свободного чата - просто отправляем сообщение без дополнительного контекста
            elif mode == 'free':
                # Для режима free можно добавить более креативный системный промпт
                context = user_message
            
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
                    'referenced_cards': [card['id'] for card in search_results],
                    'mode': mode
                }
            else:
                logger.error(f"API call failed: {response_data.get('error')}")
                return {
                    'success': False,
                    'error': response_data.get('error', 'Unknown error'),
                    'response': 'Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова.'
                }

        except Exception as e:
            logger.exception(f"AI Chat error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Произошла неожиданная ошибка при обработке вашего запроса.'
            }

    def _build_context(self, user_message: str, search_results: List[Dict], preferences: Optional[Dict]) -> str:
        """Построить контекст для отправки в API"""
        context = "Ты профессиональный консультант по недвижимости. Помогай пользователям найти идеальный дом.\n\n"
        
        # Добавить информацию о фильтрах если они есть
        if preferences and isinstance(preferences, dict) and any(v is not None for v in preferences.values()):
            context += f"Предпочтения пользователя: {json.dumps(preferences, ensure_ascii=False, indent=2)}\n\n"
        
        # Добавить найденные карточки
        if search_results:
            context += "Найденные карточки из базы данных:\n"
            for i, card in enumerate(search_results, 1):
                context += f"\n{i}. {card['title']} ({card['address']})\n"
                context += f"   Цена: {card['price']}₽ | Комнат: {card['rooms']} | Площадь: {card['area']}м²\n"
                context += f"   Рейтинг: {card['rating']}/5 | Тип: {card['house_type']}\n"
        else:
            context += "К сожалению, по вашему запросу в базе данных не найдено подходящих карточек.\n"
        
        context += f"\n\nПросьба пользователя: {user_message}"
        
        return context

    def _call_api(self, context: str) -> Dict:
        """Отправить запрос к API провайдера"""
        if not self.config or not self.client:
            return {
                'success': False,
                'error': 'API client not initialized'
            }
        
        api_methods = {
            'openai': self._call_openai,
            'anthropic': self._call_anthropic,
            'deepseek': self._call_deepseek,
        }
        
        api_method = api_methods.get(self.config.api_provider)
        if not api_method:
            error_msg = f'Unknown API provider: {self.config.api_provider}'
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
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

    def _call_deepseek(self, context: str) -> Dict:
        """Вызвать DeepSeek API (OpenAI-совместимый)"""
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
            logger.exception(f"DeepSeek API error: {e}")
            return {'success': False, 'error': str(e)}

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
