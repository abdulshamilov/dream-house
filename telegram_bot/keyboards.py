from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

STATUS_LABELS = {
    'new':      '🔴 Новая',
    'assigned': '🟠 Назначена',
    'in_work':  '🟡 В работе',
    'meeting':  '🔵 Встреча/показ',
    'deal':     '🟢 Сделка',
    'rejected': '⚫ Отказ',
}

# Статусы, в которые менеджер может переключиться из текущего
NEXT_STATUSES = {
    'new':      ['in_work', 'rejected'],
    'assigned': ['in_work', 'rejected'],
    'in_work':  ['meeting', 'rejected'],
    'meeting':  ['deal', 'rejected'],
}


def lead_admin_kb(lead_id: int) -> InlineKeyboardMarkup:
    """Кнопка 'Назначить' для уведомления руководителя о новой заявке."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='👤 Назначить', callback_data=f'assign:{lead_id}'),
    ]])


def managers_kb(lead_id: int, managers: list[dict]) -> InlineKeyboardMarkup:
    """Список менеджеров для выбора при назначении."""
    rows = []
    for m in managers:
        if not m.get('is_admin'):
            name = m['full_name']
            btn = InlineKeyboardButton(
                text=name,
                callback_data=f'assign_to:{lead_id}:{m["id"]}',
            )
            rows.append([btn])
    if not rows:
        rows.append([InlineKeyboardButton(text='Нет менеджеров', callback_data='noop')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lead_manager_kb(lead_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Кнопки смены статуса + комментарий для менеджера."""
    nexts = NEXT_STATUSES.get(current_status, [])
    rows = []
    row = []
    for s in nexts:
        row.append(InlineKeyboardButton(
            text=STATUS_LABELS.get(s, s),
            callback_data=f'status:{lead_id}:{s}',
        ))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text='💬 Комментарий', callback_data=f'comment:{lead_id}')])
    rows.append([InlineKeyboardButton(text='📋 Детали заявки', callback_data=f'lead:{lead_id}')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lead_detail_kb(lead_id: int, current_status: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Детальный просмотр заявки."""
    rows = []
    if is_admin and current_status == 'new':
        rows.append([InlineKeyboardButton(text='👤 Назначить', callback_data=f'assign:{lead_id}')])
    nexts = NEXT_STATUSES.get(current_status, [])
    for s in nexts:
        rows.append([InlineKeyboardButton(
            text=STATUS_LABELS.get(s, s),
            callback_data=f'status:{lead_id}:{s}',
        )])
    rows.append([InlineKeyboardButton(text='💬 Комментарий', callback_data=f'comment:{lead_id}')])
    return InlineKeyboardMarkup(inline_keyboard=rows)
