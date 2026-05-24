from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from .. import api
from ..keyboards import lead_admin_kb, managers_kb, STATUS_LABELS
from ..utils import format_lead

router = Router()


async def _is_admin(tg_id: int) -> bool:
    managers = await api.list_managers()
    me = next((m for m in managers if m['telegram_id'] == tg_id), None)
    return bool(me and me.get('is_admin'))


@router.message(Command('all_leads'))
async def cmd_all_leads(message: Message):
    if not await _is_admin(message.from_user.id):
        return
    leads = await api.list_leads(message.from_user.id, status='new')
    if not leads:
        await message.answer('Новых заявок нет.')
        return
    for lead in leads[:15]:
        await message.answer(
            format_lead(lead),
            parse_mode='HTML',
            reply_markup=lead_admin_kb(lead['id']) if lead['status'] == 'new' else None,
        )


@router.message(Command('stats'))
async def cmd_stats(message: Message):
    if not await _is_admin(message.from_user.id):
        return
    stats = await api.get_stats()
    by_status = stats.get('by_status', {})

    lines = [f'📊 <b>Статистика CRM</b>', f'Всего заявок: {stats.get("total", 0)}\n']
    for s, label in STATUS_LABELS.items():
        count = by_status.get(s, 0)
        if count:
            lines.append(f'{label}: {count}')

    lines.append('\n<b>Менеджеры:</b>')
    for m in stats.get('managers', []):
        if not m.get('is_admin'):
            lines.append(
                f'• {m["name"]}: всего {m["total"]}, '
                f'активных {m["active"]}, сделок {m["deals"]}'
            )

    await message.answer('\n'.join(lines), parse_mode='HTML')


# --- Назначение заявки ---

@router.callback_query(F.data.startswith('assign:'))
async def cb_assign(callback: CallbackQuery):
    if not await _is_admin(callback.from_user.id):
        await callback.answer('Нет доступа', show_alert=True)
        return
    lead_id = int(callback.data.split(':')[1])
    managers = await api.list_managers()
    active = [m for m in managers if not m.get('is_admin') and m.get('active')]
    if not active:
        await callback.answer('Нет активных менеджеров', show_alert=True)
        return
    await callback.message.answer(
        f'Выберите менеджера для заявки #{lead_id}:',
        reply_markup=managers_kb(lead_id, active),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('assign_to:'))
async def cb_assign_to(callback: CallbackQuery):
    if not await _is_admin(callback.from_user.id):
        await callback.answer('Нет доступа', show_alert=True)
        return
    _, lead_id_s, manager_id_s = callback.data.split(':')
    lead_id, manager_id = int(lead_id_s), int(manager_id_s)

    result = await api.update_lead(
        lead_id, callback.from_user.id,
        status='assigned', assigned_to=manager_id,
    )
    if result:
        managers = await api.list_managers()
        m = next((x for x in managers if x['id'] == manager_id), None)
        name = m['full_name'] if m else f'#{manager_id}'
        await callback.message.edit_text(
            f'✅ Заявка #{lead_id} назначена менеджеру <b>{name}</b>.',
            parse_mode='HTML',
        )
    else:
        await callback.answer('Ошибка при назначении', show_alert=True)
    await callback.answer()
