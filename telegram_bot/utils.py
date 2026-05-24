from .keyboards import STATUS_LABELS


def format_lead(lead: dict, show_history: bool = False) -> str:
    status = STATUS_LABELS.get(lead['status'], lead['status'])
    manager = ''
    if lead.get('assigned_to_detail'):
        manager = f"\n👤 Менеджер: {lead['assigned_to_detail']['full_name']}"

    created = lead.get('created_at', '')[:16].replace('T', ' ')

    text = (
        f"📋 <b>Заявка #{lead['id']}</b>\n"
        f"👤 {lead['name']}\n"
        f"📞 {lead['phone']}\n"
        f"🏢 {lead['jk'] or '—'}\n"
        f"📌 Статус: {status}"
        f"{manager}\n"
        f"🕐 {created}"
    )

    if show_history and lead.get('history'):
        text += '\n\n<b>История:</b>'
        for h in lead['history'][:5]:
            dt = h.get('created_at', '')[:16].replace('T', ' ')
            who = h.get('manager_name') or 'Система'
            act = h.get('action_display', h.get('action', ''))
            line = f'\n• {dt} — {who}: {act}'
            if h.get('comment'):
                line += f'\n  💬 {h["comment"]}'
            text += line

    return text
