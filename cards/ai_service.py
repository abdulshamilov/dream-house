"""
AI Service для работы с OpenAI, Anthropic и DeepSeek API
Интегрируется с базой данных карточек недвижимости
"""

import os
import json
import logging
import random
import re
from typing import Optional, List, Dict, Any, Tuple
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

    def search_cards(self, query: str, preferences: Optional[Dict] = None, limit: Optional[int] = None) -> List[Dict]:
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
        
        # Сортировка по предпочтениям пользователя
        if preferences and isinstance(preferences, dict):
            sort_by = preferences.get('sort_by')
            if sort_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-price')
            else:
                queryset = queryset.order_by('-rating', '-created_at')
        else:
            queryset = queryset.order_by('-rating', '-created_at')

        # Уникализируем по id, чтобы не было дубликатов
        cards = list(queryset)
        unique_cards = list({card.id: card for card in cards}.values())

        # Применяем лимит если указан (без рандомизации - AI сам выберет нужные)
        if limit:
            unique_cards = unique_cards[:limit]

        return [self._format_card(card) for card in unique_cards]

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
            
            logger.info(f"AI Chat called: mode={mode}, message_len={len(user_message)}")
            
            # Режим поиска квартир - ищет в БД и строит контекст с результатами
            if mode == 'search':
                # Проверить, относится ли вопрос к недвижимости
                is_realty_question = self._is_realty_related(user_message)
                
                if is_realty_question:
                    logger.info("Realty-related question detected. Searching cards...")
                    prefs = dict(user_preferences or {})
                    price_min, price_max = self._parse_price_bounds(user_message)
                    if price_min is not None:
                        prefs['price_min'] = price_min
                    if price_max is not None:
                        prefs['price_max'] = price_max

                    # Получаем все подходящие объекты, без обрезки
                    search_results = self.search_cards(user_message, prefs, limit=None)
                    logger.info(f"Found {len(search_results)} cards")
                    
                    # Если поиск не вернул результаты по запросу, показать ТОП доступные
                    if not search_results:
                        logger.info("No matching cards found. Showing top available cards.")
                        all_cards = self.Card.objects.all().order_by('-rating', '-created_at')[:5]
                        search_results = [self._format_card(card) for card in all_cards]
                    
                    context = self._build_context(user_message, search_results, user_preferences)
                    logger.info(f"Context built with {len(search_results)} cards")
                else:
                    logger.info("Question is NOT realty-related. Responding without card search.")
                    # Добавить пометку для AI что это не про недвижимость
                    context = f"[Это НЕ вопрос про недвижимость. Ответь дружелюбно на вопрос, потом предложи помощь с квартирами]\n\nВопрос: {user_message}"
            
            # Режим свободного чата - просто отправляем сообщение без дополнительного контекста
            elif mode == 'free':
                # Для режима free можно добавить более креативный системный промпт
                context = user_message
            
            # Инструктируем модель вернуть JSON с id карточек
            context_with_format = self._inject_json_instruction(context, search_results)

            # Отправить запрос к API
            logger.info(f"Calling AI API with context (with JSON instruction)...")
            response_data = self._call_api(context_with_format)
            logger.info(f"API response: success={response_data['success']}")
            
            if response_data['success']:
                parsed_json = self._try_parse_json(response_data['response'])
                ordered_ids = self._extract_card_ids(parsed_json)

                # Используем ТОЛЬКО те id, которые вернул AI
                if ordered_ids:
                    # Проверяем что AI вернул только валидные ID
                    available_ids = {card['id'] for card in search_results}
                    valid_ids = [cid for cid in ordered_ids if cid in available_ids]
                    invalid_ids = [cid for cid in ordered_ids if cid not in available_ids]
                    
                    if invalid_ids:
                        logger.warning(f"AI returned invalid card IDs: {invalid_ids}. Available: {list(available_ids)}")
                    
                    if valid_ids:
                        logger.info(f"AI selected {len(valid_ids)} valid cards: {valid_ids}")
                        referenced_ids = valid_ids
                    else:
                        logger.warning("No valid card IDs returned by AI")
                        referenced_ids = []
                else:
                    logger.warning("AI did not return valid JSON with card ids, using empty list")
                    referenced_ids = []
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
                    'response_json': parsed_json,
                    'tokens_used': response_data.get('tokens_used', 0),
                    'referenced_cards': referenced_ids,
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
        
        # Добавить найденные карточки с реальными ID
        if search_results:
            context += "Доступные варианты недвижимости:\n"
            for card in search_results:
                context += f"[ID:{card['id']}] {card['title']} - {card['address']}\n"
                context += f"   {card['price']:,}₽ | {card['rooms']}к | {card['area']}м² | ⭐{card['rating']}\n"
        else:
            context += "В базе данных пока нет карточек.\n"
        
        context += f"\nВопрос: {user_message}"
        
        return context

    def _inject_json_instruction(self, context: str, search_results: List[Dict]) -> str:
        """Добавить инструкцию возвращать JSON c отсортированными id карточек"""
        if not search_results:
            return context
        
        ids = [card['id'] for card in search_results]
        instruction = (
            "\n\n🔴 КРИТИЧЕСКИ ВАЖНАЯ ИНСТРУКЦИЯ (ОБЯЗАТЕЛЬНО ВЫПОЛНИ):\n"
            f"1. Доступные ID карточек: {ids}\n"
            "2. ⚠️ ИСПОЛЬЗУЙ ТОЛЬКО РЕАЛЬНЫЕ ID из [ID:X] - НЕ порядковые номера!\n"
            "3. СНАЧАЛА выбери 3-5 лучших карточек по ID\n"
            "4. ПОТОМ напиши текст ТОЛЬКО про эти выбранные ID\n"
            "5. В КОНЦЕ ответа верни JSON: {\"cards\": [id1, id2, id3]}\n"
            "6. ⚠️ В тексте упоминай ТОЛЬКО те ID, которые есть в JSON\n"
            "7. ⚠️ В JSON включай ТОЛЬКО те ID, про которые писал в тексте\n"
            "8. Текст и JSON должны на 100% совпадать по ID\n"
            "9. JSON должен быть на отдельной строке в самом конце\n"
            "\nПример правильного ответа (если доступны ID: 5,6,7):\n"
            "'Вот 3 лучших варианта: квартира [ID:5] за 10млн, квартира [ID:7] за 12млн, квартира [ID:6] за 8млн.\n"
            "{\"cards\": [5, 7, 6]}'\n"
        )
        return f"{context}\n{instruction}"

    def _parse_price_bounds(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Вытащить ценовой диапазон из запроса пользователя (от/до, 10м, 10-20м и т.д.)"""
        lower = None
        upper = None

        text_lower = text.lower()
        has_million_hint = 'млн' in text_lower or 'мил' in text_lower
        has_thousand_hint = 'тыс' in text_lower or 'k ' in text_lower or text_lower.endswith('k') or text_lower.endswith(' к')

        def num_to_value(raw: str, unit: Optional[str]) -> Optional[int]:
            try:
                value = float(raw.replace(',', '.'))
            except ValueError:
                return None

            unit = (unit or '').strip()
            multiplier = 1
            if unit:
                if unit in ['м', 'млн', 'мил', 'миллион', 'миллиона', 'миллионов']:
                    multiplier = 1_000_000
                elif unit in ['к', 'k', 'тыс', 'тысяч']:
                    multiplier = 1_000
            else:
                if has_million_hint or value <= 500:
                    multiplier = 1_000_000
                elif has_thousand_hint:
                    multiplier = 1_000
            return int(value * multiplier)

        # Диапазон через дефис/тире, например "10-20м"
        range_match = re.search(r"(\d+[\.,]?\d*)\s*[-–—]\s*(\d+[\.,]?\d*)\s*(млн|м|мил|миллион|миллионов|к|k|тыс)?", text_lower)
        if range_match:
            low_raw, high_raw, unit = range_match.groups()
            lower = num_to_value(low_raw, unit)
            upper = num_to_value(high_raw, unit)
            return lower, upper

        # От/до конструкции
        from_match = re.search(r"от\s*(\d+[\.,]?\d*)\s*(млн|м|мил|миллион|миллионов|к|k|тыс)?", text_lower)
        to_match = re.search(r"до\s*(\d+[\.,]?\d*)\s*(млн|м|мил|миллион|миллионов|к|k|тыс)?", text_lower)
        if from_match:
            lower = num_to_value(from_match.group(1), from_match.group(2))
        if to_match:
            upper = num_to_value(to_match.group(1), to_match.group(2))

        if lower is not None or upper is not None:
            return lower, upper

        # Одинокое число (например "квартира за 10млн" или "за 15")
        single_match = re.search(r"(\d+[\.,]?\d*)\s*(млн|м|мил|миллион|миллионов|к|k|тыс)?", text_lower)
        if single_match:
            val = num_to_value(single_match.group(1), single_match.group(2))
            if val is not None:
                lower = val

        return lower, upper

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
            # DeepSeek модель ВСЕГДА 'deepseek-chat'
            model_name = 'deepseek-chat'
            
            logger.info(f"Calling DeepSeek API with {len(context)} chars context, max_tokens={self.config.max_tokens}")
            
            # Добавляем timeout для запроса (30 секунд)
            message = self.client.chat.completions.create(
                model=model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": context}
                ],
                timeout=30.0  # 30 секунд timeout
            )

            response_text = message.choices[0].message.content
            
            # Очистить форматирование из ответа
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

    def _try_parse_json(self, text: str) -> Optional[Any]:
        """Попробовать распарсить ответ как JSON; если не получается, вернуть None"""
        if not text:
            return None
        
        # Попробовать распарсить весь текст
        try:
            return json.loads(text.strip())
        except Exception:
            pass
        
        # Попробовать найти JSON в конце текста (после последней фигурной скобки)
        try:
            last_brace = text.rfind('{')
            if last_brace != -1:
                json_part = text[last_brace:].strip()
                # Убрать возможные символы после JSON
                if json_part.count('{') == json_part.count('}'):
                    return json.loads(json_part)
        except Exception:
            pass
        
        # Попробовать найти JSON блок в markdown
        try:
            import re
            json_match = re.search(r'```(?:json)?\s*({[^`]+})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except Exception:
            pass
        
        return None

    def _extract_card_ids(self, data: Any) -> List[int]:
        """Извлечь список id карточек из JSON, ожидаем формат {cards: [ids]}"""
        ids: List[int] = []
        try:
            if isinstance(data, dict) and 'cards' in data and isinstance(data['cards'], list):
                ids = [int(x) for x in data['cards'] if isinstance(x, (int, str)) and str(x).isdigit()]
        except Exception:
            pass
        return ids

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
