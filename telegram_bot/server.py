"""
Внутренний HTTP-сервер на aiohttp.
Django сигналы → POST /notify/{event} → рассылка в Telegram.
"""
import logging
from aiohttp import web
from aiogram import Bot

from . import api, config
from .keyboards import lead_admin_kb, lead_manager_kb
from .utils import format_lead

logger = logging.getLogger(__name__)


async def _handle_notify(request: web.Request, bot: Bot) -> web.Response:
    # Validate secret
    secret = request.headers.get('X-Bot-Secret', '')
    if secret != config.API_SECRET:
        return web.Response(status=403, text='Forbidden')

    event = request.match_info['event']
    try:
        body = await request.json()
    except Exception:
        return web.Response(status=400, text='Bad JSON')

    lead_id = body.get('lead_id')
    if not lead_id:
        return web.Response(status=400, text='Missing lead_id')

    lead = await api.get_lead(lead_id)
    if not lead:
        return web.Response(status=404, text='Lead not found')

    try:
        if event == 'new_lead':
            await _notify_new_lead(bot, lead)
        elif event == 'lead_updated':
            await _notify_lead_updated(bot, lead)
    except Exception as exc:
        logger.exception('Notify error: %s', exc)

    return web.Response(text='ok')


async def _notify_new_lead(bot: Bot, lead: dict):
    """Уведомить всех админов о новой заявке."""
    managers = await api.list_managers()
    admins = [m for m in managers if m.get('is_admin')]
    text = f'🆕 <b>Новая заявка #{lead["id"]}</b>\n' + format_lead(lead)
    kb = lead_admin_kb(lead['id'])
    for admin in admins:
        try:
            await bot.send_message(admin['telegram_id'], text, parse_mode='HTML', reply_markup=kb)
        except Exception as exc:
            logger.warning('Cannot send to admin %s: %s', admin['telegram_id'], exc)


async def _notify_lead_updated(bot: Bot, lead: dict):
    """Уведомить менеджера об изменении заявки (только если изменение НЕ из бота)."""
    if not lead.get('assigned_to'):
        return
    tg_id = lead['assigned_to_detail']['telegram_id']
    status = lead['status']

    if status == 'assigned':
        text = f'📬 <b>Вам назначена заявка #{lead["id"]}</b>\n' + format_lead(lead)
    else:
        from .keyboards import STATUS_LABELS
        label = STATUS_LABELS.get(status, status)
        text = f'🔄 Заявка #{lead["id"]} обновлена — <b>{label}</b>\n' + format_lead(lead)

    kb = lead_manager_kb(lead['id'], status) if status not in ('deal', 'rejected') else None
    try:
        await bot.send_message(tg_id, text, parse_mode='HTML', reply_markup=kb)
    except Exception as exc:
        logger.warning('Cannot send to manager %s: %s', tg_id, exc)


def make_app(bot: Bot) -> web.Application:
    app = web.Application()

    async def handle(request: web.Request) -> web.Response:
        return await _handle_notify(request, bot)

    app.router.add_post('/notify/{event}', handle)
    return app


async def start_server(bot: Bot):
    app = make_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.NOTIFY_HOST, config.NOTIFY_PORT)
    await site.start()
    logger.info('Notify server started on %s:%s', config.NOTIFY_HOST, config.NOTIFY_PORT)
    return runner
