from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .. import api
from ..states import SearchState
from ..utils import format_lead

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    managers = await api.list_managers()

    if managers is None or (isinstance(managers, list) and len(managers) == 0 and not managers):
        await message.answer(
            '⚠️ Сервер недоступен. Убедитесь что Django запущен на порту 8000.'
        )
        return

    me = next((m for m in managers if m['telegram_id'] == tg_id), None)

    if not me:
        await message.answer(
            f'❌ Ваш Telegram ID: <code>{tg_id}</code>\n\n'
            'Вы не зарегистрированы в системе.\n'
            'Передайте этот ID администратору для добавления в CRM.',
            parse_mode='HTML',
        )
        return

    role = '👑 Руководитель' if me['is_admin'] else '👤 Менеджер'
    await message.answer(
        f'Добро пожаловать, <b>{me["full_name"]}</b>!\n'
        f'Роль: {role}\n\n'
        'Команды:\n'
        '/my_leads — мои заявки\n'
        '/search — поиск по имени/телефону\n'
        + ('/all_leads — все заявки\n/stats — статистика команды' if me['is_admin'] else ''),
        parse_mode='HTML',
    )


@router.message(Command('me'))
async def cmd_me(message: Message):
    tg_id = message.from_user.id
    managers = await api.list_managers()

    if managers is None or not isinstance(managers, list):
        await message.answer(f'⚠️ API недоступен. Ваш Telegram ID: <code>{tg_id}</code>', parse_mode='HTML')
        return

    me = next((m for m in managers if m['telegram_id'] == tg_id), None)

    lines = [f'🔍 <b>Ваш Telegram ID:</b> <code>{tg_id}</code>']
    if me:
        role = '👑 Руководитель' if me['is_admin'] else '👤 Менеджер'
        lines.append(f'✅ Вы в системе: <b>{me["full_name"]}</b> — {role}')
        lines.append(f'Активен: {"да" if me.get("active") else "нет"}')
    else:
        lines.append('❌ Вас нет в базе менеджеров')

    lines.append(f'\n📋 Менеджеры в системе ({len(managers)}):')
    for m in managers:
        role = '👑' if m['is_admin'] else '👤'
        active = '✅' if m.get('active') else '🚫'
        lines.append(f'{active}{role} {m["full_name"]} — ID: <code>{m["telegram_id"]}</code>')

    await message.answer('\n'.join(lines), parse_mode='HTML')


@router.message(Command('search'))
async def cmd_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await message.answer('🔍 Введите имя или телефон для поиска:')


@router.message(SearchState.waiting_query)
async def process_search(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id
    leads = await api.list_leads(tg_id, q=message.text.strip())
    if not leads:
        await message.answer('Ничего не найдено.')
        return
    for lead in leads[:10]:
        await message.answer(format_lead(lead), parse_mode='HTML')
