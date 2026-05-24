"""HTTP client for DRF API. All methods are async."""
import logging
import aiohttp
from . import config

logger = logging.getLogger(__name__)

HEADERS = {
    'X-Bot-Secret': config.API_SECRET,
    'Content-Type': 'application/json',
}


def _manager_headers(telegram_id: int) -> dict:
    return {**HEADERS, 'X-Telegram-Id': str(telegram_id)}


async def _get(url: str, headers: dict, params: dict = None) -> dict | list | None:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status == 200:
                    return await r.json()
                logger.warning('GET %s → %s', url, r.status)
    except Exception as exc:
        logger.error('API GET error %s: %s', url, exc)
    return None


async def _patch(url: str, headers: dict, data: dict) -> dict | None:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.patch(url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status == 200:
                    return await r.json()
                text = await r.text()
                logger.warning('PATCH %s → %s: %s', url, r.status, text[:200])
    except Exception as exc:
        logger.error('API PATCH error %s: %s', url, exc)
    return None


async def get_lead(lead_id: int, telegram_id: int | None = None) -> dict | None:
    headers = _manager_headers(telegram_id) if telegram_id else HEADERS
    result = await _get(f'{config.API_BASE_URL}/api/leads/{lead_id}/', headers)
    return result if isinstance(result, dict) else None


async def list_leads(telegram_id: int, q: str = '', status: str = '', overdue: bool = False) -> list[dict]:
    params: dict = {}
    if q:
        params['q'] = q
    if status:
        params['status'] = status
    if overdue:
        params['overdue'] = 'true'
    result = await _get(f'{config.API_BASE_URL}/api/leads/', _manager_headers(telegram_id), params)
    if isinstance(result, dict):
        return result.get('results', [])
    return result if isinstance(result, list) else []


async def update_lead(lead_id: int, telegram_id: int, **kwargs) -> dict | None:
    return await _patch(
        f'{config.API_BASE_URL}/api/leads/{lead_id}/',
        _manager_headers(telegram_id),
        kwargs,
    )


async def list_managers() -> list[dict]:
    result = await _get(f'{config.API_BASE_URL}/api/leads/managers/', HEADERS)
    if isinstance(result, dict):
        return result.get('results', [])
    return result if isinstance(result, list) else []


async def get_stats() -> dict:
    result = await _get(f'{config.API_BASE_URL}/api/leads/stats/', HEADERS)
    return result if isinstance(result, dict) else {}
