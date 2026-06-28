from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import api
from ..keyboards import lead_manager_kb, lead_detail_kb, STATUS_LABELS
from ..states import CommentState
from ..utils import format_lead

router = Router()


@router.message(Command('my_leads'))
async def cmd_my_leads(message: Message):
    tg_id = message.from_user.id
    leads = await api.list_leads(tg_id)
    if not leads:
        await message.answer('У вас нет активных заявок.')
        return
    for lead in leads[:15]:
        kb = lead_manager_kb(lead['id'], lead['status'])
        await message.answer(format_lead(lead), parse_mode='HTML', reply_markup=kb)


# --- Просмотр детальной заявки ---

@router.callback_query(F.data.startswith('lead:'))
async def cb_lead_detail(callback: CallbackQuery):
    lead_id = int(callback.data.split(':')[1])
    tg_id = callback.from_user.id
    lead = await api.get_lead(lead_id, tg_id)
    if not lead:
        await callback.answer('Заявка не найдена', show_alert=True)
        return

    managers = await api.list_managers()
    me = next((m for m in managers if m['telegram_id'] == tg_id), None)
    is_admin = bool(me and me.get('is_admin'))

    await callback.message.answer(
        format_lead(lead, show_history=True),
        parse_mode='HTML',
        reply_markup=lead_detail_kb(lead['id'], lead['status'], is_admin),
    )
    await callback.answer()


# --- Смена статуса ---

@router.callback_query(F.data.startswith('status:'))
async def cb_status_change(callback: CallbackQuery):
    parts = callback.data.split(':')
    lead_id, new_status = int(parts[1]), parts[2]
    tg_id = callback.from_user.id

    result = await api.update_lead(lead_id, tg_id, status=new_status)
    if result:
        label = STATUS_LABELS.get(new_status, new_status)
        await callback.message.edit_text(
            f'✅ Статус заявки #{lead_id} изменён: <b>{label}</b>\n\n'
            + format_lead(result),
            parse_mode='HTML',
            reply_markup=lead_manager_kb(lead_id, new_status) if new_status not in ('deal', 'rejected') else None,
        )
        await callback.answer()
    else:
        await callback.answer('Ошибка при изменении статуса', show_alert=True)


# --- Комментарий (FSM) ---

@router.callback_query(F.data.startswith('comment:'))
async def cb_comment_start(callback: CallbackQuery, state: FSMContext):
    lead_id = int(callback.data.split(':')[1])
    await state.set_state(CommentState.waiting_text)
    await state.update_data(lead_id=lead_id)
    await callback.message.answer(f'✏️ Введите комментарий к заявке #{lead_id}:')
    await callback.answer()


@router.message(CommentState.waiting_text)
async def process_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    lead_id = data['lead_id']
    tg_id = message.from_user.id
    text = message.text.strip()

    result = await api.update_lead(lead_id, tg_id, comment=text)
    if result:
        await message.answer(f'✅ Комментарий к заявке #{lead_id} сохранён.')
    else:
        await message.answer('❌ Не удалось сохранить комментарий.')


# --- Нет операции (заглушка для кнопок-заголовков) ---

@router.callback_query(F.data == 'noop')
async def cb_noop(callback: CallbackQuery):
    await callback.answer()
