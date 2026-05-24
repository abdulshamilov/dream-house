import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot

from . import api, config
from .keyboards import lead_admin_kb
from .utils import format_lead

logger = logging.getLogger(__name__)

NOTIFY_HOUR: int = int(getattr(config, 'OVERDUE_NOTIFY_HOUR', 9))


def _seconds_until_next(hour: int) -> float:
    now = datetime.now()
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def _send_overdue_report(bot: Bot) -> None:
    managers = await api.list_managers()
    admins = [m for m in managers if m.get('is_admin') and m.get('active', True)]
    if not admins:
        return

    leads = await api.list_leads(admins[0]['telegram_id'], overdue=True)
    if not leads:
        logger.info('Overdue report: no overdue leads')
        return

    header = f'⚠️ <b>Просроченные заявки: {len(leads)}</b>\nНет движения более 2 дней:\n'

    for admin in admins:
        try:
            await bot.send_message(admin['telegram_id'], header)
            for lead in leads[:20]:
                await bot.send_message(
                    admin['telegram_id'],
                    format_lead(lead),
                    parse_mode='HTML',
                    reply_markup=lead_admin_kb(lead['id']),
                )
            logger.info('Overdue report sent to admin %s (%s leads)', admin['name'], len(leads))
        except Exception as exc:
            logger.error('Failed to notify admin %s: %s', admin['telegram_id'], exc)


async def run_scheduler(bot: Bot) -> None:
    logger.info('Scheduler started — daily overdue report at %02d:00', NOTIFY_HOUR)
    while True:
        delay = _seconds_until_next(NOTIFY_HOUR)
        logger.info('Next overdue report in %.0f seconds', delay)
        await asyncio.sleep(delay)
        await _send_overdue_report(bot)
        await asyncio.sleep(60)  # защита от двойного срабатывания
