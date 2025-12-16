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
        
        # Применить предпочтения пользователя (фильтрация) - ПЕРВЫЙ ПРИОРИТЕТ
        if preferences and isinstance(preferences, dict) and any(v is not None for v in preferences.values()):
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
        
        # Полнотекстовый поиск по ключевым словам (только если есть query)
        # Но НЕ если мы уже фильтровали по параметрам
        if query and query.strip() and (not preferences or not any(v is not None for v in preferences.values())):
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

    def _parse_price_from_text(self, text: str) -> tuple:
        """
        Парсить ограничения по цене из текста
        Возвращает кортеж (price_min, price_max)
        
        Примеры:
        - "до 2млн" -> (None, 2000000)
        - "от 1млн до 3млн" -> (1000000, 3000000)
        - "2000000" -> (None, 2000000)
        """
        import re
        
        text_lower = text.lower()
        price_min, price_max = None, None
        
        # Ищем "до X млн" или "до X миллионов"
        match_max = re.search(r'до\s+(\d+(?:[.,]\d+)?)\s*(?:млн|миллион)', text_lower)
        if match_max:
            max_val = float(match_max.group(1).replace(',', '.'))
            price_max = int(max_val * 1_000_000)
        
        # Ищем "от X млн"
        match_min = re.search(r'от\s+(\d+(?:[.,]\d+)?)\s*(?:млн|миллион)', text_lower)
        if match_min:
            min_val = float(match_min.group(1).replace(',', '.'))
            price_min = int(min_val * 1_000_000)
        
        # Ищем диапазон "X млн до Y млн"
        match_range = re.search(r'(\d+(?:[.,]\d+)?)\s*млн\s+до\s+(\d+(?:[.,]\d+)?)\s*млн', text_lower)
        if match_range:
            min_val = float(match_range.group(1).replace(',', '.'))
            max_val = float(match_range.group(2).replace(',', '.'))
            price_min = int(min_val * 1_000_000)
            price_max = int(max_val * 1_000_000)
        
        # Ищем "в районе X млн" или "около X млн"
        match_around = re.search(r'(?:в районе|около)\s+(\d+(?:[.,]\d+)?)\s*млн', text_lower)
        if match_around:
            val = float(match_around.group(1).replace(',', '.'))
            center = int(val * 1_000_000)
            # ±20% от значения
            price_min = int(center * 0.8)
            price_max = int(center * 1.2)
        
        return price_min, price_max

    def _parse_rooms_from_text(self, text: str) -> Optional[int]:
        """
        Парсить количество комнат из текста
        Примеры: "1-комнатная", "двухкомнатная", "3 комнаты"
        """
        import re
        
        text_lower = text.lower()
        
        # Ищем "X-комнатная", "Xк"
        match = re.search(r'(\d+)\s*[к-]*комнатн', text_lower)
        if match:
            return int(match.group(1))
        
        # Ищем словесные обозначения
        word_map = {
            'однокомнатн': 1,
            'двухкомнатн': 2,
            'трехкомнатн': 3,
            'четырехкомнатн': 4,
            'пятикомнатн': 5,
        }
        
        for word, rooms in word_map.items():
            if word in text_lower:
                return rooms
        
        return None

    def _parse_city_from_text(self, text: str) -> Optional[int]:
        """
        Парсить город из текста
        Возвращает ID города или None
        """
        text_lower = text.lower()
        
        city_map = {
            'махачкала': 1,
            'махачкале': 1,
            'каспийск': 2,
            'каспийске': 2,
            'дербент': 3,
            'дербенте': 3,
        }
        
        for city_name, city_id in city_map.items():
            if city_name in text_lower:
                return city_id
        
        return None

    def _parse_house_type_from_text(self, text: str) -> Optional[str]:
        """
        Парсить тип дома из текста
        Возвращает тип дома: 'apartment', 'house', 'townhouse' и т.д.
        """
        text_lower = text.lower()
        
        type_map = {
            'квартира': 'apartment',
            'дом': 'house',
            'коттедж': 'house',
            'таунхаус': 'townhouse',
            'студия': 'studio',
            'офис': 'office',
        }
        
        for type_name, type_code in type_map.items():
            if type_name in text_lower:
                return type_code
        
        return None

    def _is_realty_related(self, text: str) -> bool:
        """
        Проверить, относится ли вопрос к недвижимости/квартирам
        """
        realty_keywords = [
            'квартира', 'квартиры', 'квартир', 'квартире', 'квартирам',
            'дом', 'дома', 'домов', 'доме', 'домам',
            'недвижимость', 'недвижимости',
            'апартамент', 'апартаменты',
            'коттедж', 'коттеджи',
            'офис', 'офисы',
            'студия', 'студии',
            'двухкомнатн', 'трехкомнатн', 'четырехкомнатн',
            'комната', 'комнаты', 'комнат',
            'площадь', 'метры', 'метров', 'м²',
            'цена', 'стоимость', 'рублей', '₽',
            'этаж', 'этажность',
            'балкон', 'балконы',
            'парковка', 'парковки',
            'лифт', 'лифты', 'лифта',
            'ремонт', 'отремонтирова',
            'мебель', 'мебелирова',
            'город', 'махачкала', 'каспийск', 'дербент',
            'район', 'районе',
            'купить', 'продать', 'сдать', 'снять',
            'аренда', 'аренде',
            'ипотека', 'ипотеку', 'ипотекой',
            'кредит',
            'застройщик', 'разработчик',
            'документ', 'документы',
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in realty_keywords)

    def _needs_recommendations(self, text: str) -> bool:
        """
        ✅ НОВОЕ: Определить нужны ли рекомендации квартир в ответе
        
        Возвращает True если пользователь просит рекомендации/подборку
        """
        recommendation_keywords = [
            'рекомендуй', 'рекомендация',
            'предложи', 'предложение',
            'показа', 'покажи', 'показать',
            'найди', 'найти', 'ищу', 'ищите',
            'подбери', 'подборка',
            'какие квартиры', 'какие варианты',
            'есть ли', 'есть', 'имеетесь',
            'подходит', 'подходящие',
            'лучше', 'хорошие', 'качественные',
            'похожие', 'подобные',
            'интересуюсь', 'интересует', 'интересуют',
            'хочу', 'хотим', 'хотят',
            'нужна', 'нужны', 'нужен',
            'ищу квартиру', 'ищу дом',
            'ищу апартамент',
        ]
        
        text_lower = text.lower()
        # Если вопрос про недвижимость И есть хотя бы одно ключевое слово поиска
        return self._is_realty_related(text) and any(
            keyword in text_lower for keyword in recommendation_keywords
        )

    def _smart_search_with_fallback(self, user_message: str, preferences: Dict) -> List[Dict]:
        """
        ✅ НОВОЕ: Умный поиск с нескольными уровнями fallback
        
        1. Попытка с парсанными фильтрами
        2. Fallback на менее строгие фильтры
        3. Поиск по тексту без фильтров
        4. Топ рейтинг-рейтинговых вариантов
        """
        import re
        
        # Парсить параметры из текста, если они не переданы
        if not preferences:
            preferences = {}
        
        # Парсить цену из текста
        price_min, price_max = self._parse_price_from_text(user_message)
        if price_min is not None:
            preferences['price_min'] = price_min
        if price_max is not None:
            preferences['price_max'] = price_max
        
        # Парсить комнаты из текста
        rooms = self._parse_rooms_from_text(user_message)
        if rooms is not None:
            preferences['rooms'] = rooms
        
        # Парсить город из текста
        city = self._parse_city_from_text(user_message)
        if city is not None:
            preferences['city'] = city
        
        # Парсить тип дома из текста
        house_type = self._parse_house_type_from_text(user_message)
        if house_type is not None:
            preferences['house_type'] = house_type
        
        logger.info(f"🔍 Parsed preferences: {preferences}")
        
        # ✅ Уровень 1: Попытка с ВСЕ фильтрами (максимально строгий)
        if any(v is not None for v in preferences.values()):
            search_results = self.search_cards(user_message, preferences, limit=6)
            if search_results:
                logger.info(f"✅ Level 1: Found {len(search_results)} cards with all filters")
                return search_results
        
        # ✅ Уровень 2: Попытка с ОСНОВНЫМИ фильтрами (без опциональных)
        main_preferences = {
            k: v for k, v in preferences.items() 
            if k in ['city', 'rooms', 'house_type'] and v is not None
        }
        if main_preferences:
            search_results = self.search_cards(user_message, main_preferences, limit=6)
            if search_results:
                logger.info(f"✅ Level 2: Found {len(search_results)} cards with main filters")
                return search_results
        
        # ✅ Уровень 3: Попытка БЕЗ фильтров (по тексту с рейтингом)
        logger.info("➡️ Level 3: Searching without filters (text-based)")
        search_results = self.search_cards(user_message, preferences=None, limit=6)
        if search_results:
            logger.info(f"✅ Level 3: Found {len(search_results)} cards by text")
            return search_results
        
        # ✅ Уровень 4: Полная fallback - Топ рейтинговые карточки
        logger.info("⚠️ Level 4: No matches. Returning top rated apartments")
        try:
            top_cards = self.Card.objects.all().order_by('-rating', '-created_at')[:6]
            return [self._format_card(card) for card in top_cards]
        except Exception as e:
            logger.error(f"Error in Level 4 fallback: {e}")
            return []

    def chat(self, user_message: str, user_preferences: Optional[Dict] = None, user_id: Optional[int] = None, mode: str = 'search', chat_history: Optional[List[Dict]] = None) -> Dict:
        """
        Отправить сообщение AI и получить ответ с автоматическим распознаванием нужды в рекомендациях
        
        Args:
            user_message: Сообщение от пользователя
            user_preferences: Предпочтения пользователя для режима поиска
            user_id: ID пользователя для сохранения истории
            mode: 'search' - автоматический поиск, 'free' - обычный чат
        
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
            
            logger.info(f"AI Chat called: mode={mode}, message_len={len(user_message)}")
            
            # ✅ НОВОЕ: Автоматическое распознавание когда нужны рекомендации
            is_realty_question = self._is_realty_related(user_message)
            needs_recommendations = self._needs_recommendations(user_message)
            
            # Режим 'search' - УМНЫЙ РЕЖИМ с автоматическим поиском
            if mode == 'search' or (is_realty_question and needs_recommendations):
                
                if is_realty_question:
                    logger.info("🏠 Realty-related question detected. Smart search enabled.")
                    
                    # Парсить параметры из текста, если они не переданы
                    if not user_preferences:
                        user_preferences = {}
                    
                    # ✅ УЛУЧШЕНО: Более гибкий парсинг с fallback
                    search_results = self._smart_search_with_fallback(
                        user_message, 
                        user_preferences
                    )
                    
                    logger.info(f"Found {len(search_results)} cards")
                    
                    if search_results:
                        context = self._build_context(user_message, search_results, user_preferences)
                        logger.info(f"Context built with {len(search_results)} cards")
                    else:
                        # Совсем ничего не нашли - предложить уточнить
                        context = f"[Нет вариантов по запросу: {user_message}. Предложи уточнить: другой район, другой бюджет, расширить поиск. Будь дружелюбным и конкретным.]"
                
                else:
                    logger.info("❓ Question is NOT realty-related but search mode enabled")
                    # Не про недвижимость, но запрошен режим search
                    context = f"[Это НЕ вопрос про недвижимость. Ответь дружелюбно на вопрос, потом предложи помощь с поиском квартир]\n\nВопрос: {user_message}"
            
            # Режим 'free' - обычный чат БЕЗ обязательного поиска
            elif mode == 'free':
                # Для режима free можно добавить более креативный системный промпт
                context = user_message
            
            # Добавить историю чата если есть user_id
            if user_id:
                history_context = self._get_chat_history(user_id, limit=10)
                if history_context:
                    context = f"{history_context}\nТекущий запрос: {context}"
            
            # Отправить запрос к API
            logger.info(f"Calling AI API with context...")
            response_data = self._call_api(context, chat_history, user_message)
            logger.info(f"API response: success={response_data['success']}")
            
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
        context = ""
        
        # Добавить информацию о фильтрах если они есть
        if preferences and isinstance(preferences, dict) and any(v is not None for v in preferences.values()):
            context += f"Фильтры пользователя: {json.dumps(preferences, ensure_ascii=False)}\n\n"
        
        # Добавить найденные карточки
        if search_results:
            context += "Доступные варианты недвижимости:\n"
            for i, card in enumerate(search_results, 1):
                context += f"{i}. {card['title']} - {card['address']}\n"
                context += f"   {card['price']:,}₽ | {card['rooms']}к | {card['area']}м² | ⭐{card['rating']}\n"
        else:
            context += "В базе данных пока нет карточек.\n"
        
        context += f"\nВопрос: {user_message}"
        
        return context

    def _call_api(self, context: str, chat_history: Optional[List[Dict]] = None, user_message: str = "") -> Dict:
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
        
        return api_method(context, chat_history, user_message)

    def _build_messages_with_history(self, context: str, chat_history: Optional[List[Dict]] = None, user_message: str = "") -> List[Dict]:
        """Построить список сообщений с историей для API"""
        messages = [{"role": "system", "content": self.config.system_prompt}]
        
        # Добавить историю чата если она есть
        if chat_history:
            for msg in chat_history[-5:]:  # Последние 5 сообщений для контекста
                if 'role' in msg and 'content' in msg:
                    messages.append(msg)
        
        # Добавить текущее сообщение (с контекстом поиска если нужно)
        messages.append({"role": "user", "content": context})
        
        return messages

    def _call_openai(self, context: str, chat_history: Optional[List[Dict]] = None, user_message: str = "") -> Dict:
        """Вызвать OpenAI API"""
        try:
            messages = self._build_messages_with_history(context, chat_history, user_message)
            
            message = self.client.chat.completions.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages
            )

            return {
                'success': True,
                'response': message.choices[0].message.content,
                'tokens_used': message.usage.total_tokens
            }

        except Exception as e:
            logger.exception(f"OpenAI API error: {e}")
            return {'success': False, 'error': str(e)}

    def _call_anthropic(self, context: str, chat_history: Optional[List[Dict]] = None, user_message: str = "") -> Dict:
        """Вызвать Anthropic Claude API"""
        try:
            messages = self._build_messages_with_history(context, chat_history, user_message)
            
            # Для Anthropic нужно отделить system от остальных messages
            system_msg = messages[0]['content'] if messages and messages[0]['role'] == 'system' else self.config.system_prompt
            user_messages = messages[1:] if len(messages) > 1 else [{"role": "user", "content": context}]
            
            message = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                system=system_msg,
                messages=user_messages,
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

    def _call_deepseek(self, context: str, chat_history: Optional[List[Dict]] = None, user_message: str = "") -> Dict:
        """Вызвать DeepSeek API (OpenAI-совместимый)"""
        try:
            # DeepSeek модель ВСЕГДА 'deepseek-chat'
            model_name = 'deepseek-chat'
            
            messages = self._build_messages_with_history(context, chat_history, user_message)
            
            logger.info(f"Calling DeepSeek API with {len(context)} chars context, {len(messages)} messages, max_tokens={self.config.max_tokens}")
            
            # Добавляем timeout для запроса (30 секунд)
            message = self.client.chat.completions.create(
                model=model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                timeout=30.0  # 30 секунд timeout
            )

            response_text = message.choices[0].message.content
            
            # Очистить форматирование из ответа
            response_text = self._clean_response(response_text)
            
            tokens_used = getattr(message.usage, 'total_tokens', self.config.max_tokens)
            
            logger.info(f"DeepSeek response: {len(response_text)} chars, {tokens_used} tokens")

            return {
                'success': True,
                'response': response_text,
                'tokens_used': tokens_used
            }

        except Exception as e:
            logger.exception(f"DeepSeek API error: {e}")
            return {'success': False, 'error': str(e)}

    def _clean_response(self, text: str) -> str:
        """Очистить ответ от markdown и лишнего форматирования"""
        # Убрать ** (жирный текст)
        text = text.replace('**', '')
        
        # Убрать ## (заголовки)
        text = text.replace('##', '')
        
        # Убрать # (заголовки)
        text = text.replace('# ', '')
        
        # Убрать литеральные \n (если есть в виде текста)
        text = text.replace('\\n', '\n')
        
        # Убрать ```` (блоки кода)
        text = text.replace('```', '')
        text = text.replace('`', '')
        
        # Убрать пробелы в начале и конце каждой строки
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        # Убрать пустые строки
        text = '\n'.join([line for line in text.split('\n') if line.strip()])
        
        return text

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

    def _get_chat_history(self, user_id: int, limit: int = 10) -> str:
        """Получить последние N сообщений из истории для контекста"""
        try:
            from .models import ChatMessage
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            messages = ChatMessage.objects.filter(user=user).order_by('-created_at')[:limit]
            
            if not messages:
                return ""
            
            # Формируем текст истории в обратном порядке (старые → новые)
            history = "История предыдущих сообщений:\n"
            for msg in reversed(messages):
                history += f"Пользователь: {msg.message[:100]}...\n" if len(msg.message) > 100 else f"Пользователь: {msg.message}\n"
                if msg.response:
                    history += f"Ассистент: {msg.response[:100]}...\n\n" if len(msg.response) > 100 else f"Ассистент: {msg.response}\n\n"
            
            return history
        except Exception as e:
            logger.warning(f"Failed to get chat history: {e}")
            return ""
            return None
