"""
Universal API Proxy Server
Разворачивается на голландском сервере для обхода блокировок
Поддерживает: OpenAI, Anthropic, и другие API

Дополнительно: кеширование ответов, health-мониторинг
"""

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os
import logging
import hashlib
import json
import time
from functools import wraps

app = Flask(__name__)
CORS(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API ключи хранятся ТОЛЬКО на этом сервере
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
PROXY_SECRET_KEY = os.environ.get('PROXY_SECRET_KEY', 'your-secret-key-here')

# URLs провайдеров
OPENAI_BASE_URL = "https://api.openai.com"
ANTHROPIC_BASE_URL = "https://api.anthropic.com"

# Простой in-memory кеш (для экономии на повторных запросах)
# В продакшене лучше Redis
CACHE = {}
CACHE_TTL = int(os.environ.get('CACHE_TTL', 3600))  # 1 час по умолчанию
CACHE_ENABLED = os.environ.get('CACHE_ENABLED', 'true').lower() == 'true'


def verify_request():
    """Проверка авторизации запроса от основного сервера"""
    auth_header = request.headers.get('X-Proxy-Auth')
    if not auth_header or auth_header != PROXY_SECRET_KEY:
        return False
    return True


def get_cache_key(provider: str, path: str, body: bytes) -> str:
    """Генерация ключа кеша"""
    content = f"{provider}:{path}:{body.decode('utf-8', errors='ignore')}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_response(cache_key: str):
    """Получить ответ из кеша"""
    if not CACHE_ENABLED:
        return None
    cached = CACHE.get(cache_key)
    if cached and time.time() - cached['time'] < CACHE_TTL:
        logger.info(f"Cache HIT: {cache_key[:16]}...")
        return cached['data']
    return None


def set_cached_response(cache_key: str, data: dict):
    """Сохранить ответ в кеш"""
    if CACHE_ENABLED:
        CACHE[cache_key] = {'data': data, 'time': time.time()}
        # Очистка старых записей (простая стратегия)
        if len(CACHE) > 1000:
            oldest = sorted(CACHE.items(), key=lambda x: x[1]['time'])[:500]
            for key, _ in oldest:
                del CACHE[key]


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'openai_configured': bool(OPENAI_API_KEY),
        'anthropic_configured': bool(ANTHROPIC_API_KEY),
        'cache_enabled': CACHE_ENABLED,
        'cache_size': len(CACHE)
    })


@app.route('/stats', methods=['GET'])
def stats():
    """Статистика прокси (требует авторизации)"""
    if not verify_request():
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'cache_entries': len(CACHE),
        'cache_ttl': CACHE_TTL,
        'providers': {
            'openai': bool(OPENAI_API_KEY),
            'anthropic': bool(ANTHROPIC_API_KEY)
        }
    })


@app.route('/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_openai(path):
    """
    Проксирование запросов к OpenAI API
    Все запросы к /v1/* перенаправляются на https://api.openai.com/v1/*
    """
    # Проверка авторизации
    if not verify_request():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not OPENAI_API_KEY:
        return jsonify({'error': 'OpenAI API key not configured on proxy server'}), 500
    
    # Проверка кеша для POST запросов к chat/completions (без stream)
    body = request.get_data()
    cache_key = None
    
    if request.method == 'POST' and 'chat/completions' in path:
        try:
            body_json = json.loads(body)
            # Кешируем только не-стриминговые запросы
            if not body_json.get('stream', False):
                cache_key = get_cache_key('openai', path, body)
                cached = get_cached_response(cache_key)
                if cached:
                    return jsonify(cached)
        except json.JSONDecodeError:
            pass
    
    # Формируем URL для OpenAI
    target_url = f"{OPENAI_BASE_URL}/v1/{path}"
    
    # Копируем заголовки, заменяя авторизацию на реальный ключ OpenAI
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
    }
    
    # Опционально копируем другие заголовки OpenAI
    for header in ['OpenAI-Organization', 'OpenAI-Project']:
        if header in request.headers:
            headers[header] = request.headers[header]
    
    try:
        # Делаем запрос к OpenAI
        logger.info(f"Proxying request to: {target_url}")
        
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=body,
            params=request.args,
            stream=True,
            timeout=120  # 2 минуты таймаут для долгих запросов
        )
        
        # Для не-стриминговых успешных ответов — кешируем
        if cache_key and response.status_code == 200:
            try:
                response_data = response.json()
                set_cached_response(cache_key, response_data)
                return jsonify(response_data)
            except:
                pass
        
        # Для streaming ответов
        def generate():
            for chunk in response.iter_content(chunk_size=1024):
                yield chunk
        
        # Возвращаем ответ с тем же статусом и заголовками
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in response.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(
            generate(),
            status=response.status_code,
            headers=response_headers,
            content_type=response.headers.get('Content-Type')
        )
        
    except requests.exceptions.Timeout:
        logger.error("Request to OpenAI timed out")
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to OpenAI failed: {e}")
        return jsonify({'error': str(e)}), 502


# ==================== ANTHROPIC PROXY ====================

@app.route('/anthropic/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_anthropic(path):
    """
    Проксирование запросов к Anthropic API
    Все запросы к /anthropic/* перенаправляются на https://api.anthropic.com/*
    """
    if not verify_request():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not ANTHROPIC_API_KEY:
        return jsonify({'error': 'Anthropic API key not configured on proxy server'}), 500
    
    body = request.get_data()
    cache_key = None
    
    # Кеширование для messages API
    if request.method == 'POST' and 'messages' in path:
        try:
            body_json = json.loads(body)
            if not body_json.get('stream', False):
                cache_key = get_cache_key('anthropic', path, body)
                cached = get_cached_response(cache_key)
                if cached:
                    return jsonify(cached)
        except json.JSONDecodeError:
            pass
    
    target_url = f"{ANTHROPIC_BASE_URL}/{path}"
    
    headers = {
        'x-api-key': ANTHROPIC_API_KEY,
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
        'anthropic-version': request.headers.get('anthropic-version', '2023-06-01'),
    }
    
    try:
        logger.info(f"Proxying request to Anthropic: {target_url}")
        
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=body,
            params=request.args,
            stream=True,
            timeout=120
        )
        
        if cache_key and response.status_code == 200:
            try:
                response_data = response.json()
                set_cached_response(cache_key, response_data)
                return jsonify(response_data)
            except:
                pass
        
        def generate():
            for chunk in response.iter_content(chunk_size=1024):
                yield chunk
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in response.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(
            generate(),
            status=response.status_code,
            headers=response_headers,
            content_type=response.headers.get('Content-Type')
        )
        
    except requests.exceptions.Timeout:
        logger.error("Request to Anthropic timed out")
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Anthropic failed: {e}")
        return jsonify({'error': str(e)}), 502


# ==================== CACHE MANAGEMENT ====================

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Очистить кеш (требует авторизации)"""
    if not verify_request():
        return jsonify({'error': 'Unauthorized'}), 401
    
    count = len(CACHE)
    CACHE.clear()
    return jsonify({'cleared': count})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"Starting Universal API Proxy Server on port {port}")
    print(f"OpenAI API Key configured: {bool(OPENAI_API_KEY)}")
    print(f"Anthropic API Key configured: {bool(ANTHROPIC_API_KEY)}")
    print(f"Caching enabled: {CACHE_ENABLED}, TTL: {CACHE_TTL}s")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
