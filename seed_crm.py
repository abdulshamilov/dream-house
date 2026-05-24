import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.stdout = open(os.devnull, 'w')  # silence all output
django.setup()
sys.stdout = sys.__stdout__

from crm.models import Manager, Lead, LeadHistory
from django.utils import timezone
from datetime import timedelta

managers_data = [
    {'name': 'Magomed Aliev',   'telegram_id': 111111111, 'telegram_username': 'magomed_a',  'is_admin': False},
    {'name': 'Patimat Isaeva',  'telegram_id': 222222222, 'telegram_username': 'patimat_i',  'is_admin': False},
    {'name': 'Shamil Kurbanov', 'telegram_id': 333333333, 'telegram_username': 'shamil_k',   'is_admin': False},
]
managers = []
for d in managers_data:
    m, _ = Manager.objects.get_or_create(telegram_id=d['telegram_id'], defaults=d)
    managers.append(m)

leads_data = [
    {'name': 'Ali Magomedov',    'phone': '+79281234567', 'jk': 'ZhK Premium',    'status': 'new',      'source': 'site_form'},
    {'name': 'Zarema Gadzhieva', 'phone': '+79282345678', 'jk': 'ZhK Kaspiy',     'status': 'assigned', 'assigned_to': managers[0], 'source': 'call_request'},
    {'name': 'Rasul Omarov',     'phone': '+79283456789', 'jk': 'ZhK Centralny',  'status': 'in_work',  'assigned_to': managers[1], 'source': 'site_form'},
    {'name': 'Khadizhat M.',     'phone': '+79284567890', 'jk': 'ZhK Yuzhny',     'status': 'meeting',  'assigned_to': managers[0], 'source': 'site_form'},
    {'name': 'Ibragim D.',       'phone': '+79285678901', 'jk': 'ZhK Premium',    'status': 'deal',     'assigned_to': managers[2], 'source': 'call_request'},
    {'name': 'Ummu Magomedova',  'phone': '+79286789012', 'jk': 'ZhK Kaspiy',     'status': 'rejected', 'assigned_to': managers[1], 'source': 'site_form'},
    {'name': 'Kamil Abdullaev',  'phone': '+79287890123', 'jk': 'ZhK Centralny',  'status': 'new',      'source': 'site_form'},
    {'name': 'Saida Alieva',     'phone': '+79288901234', 'jk': 'ZhK Yuzhny',     'status': 'assigned', 'assigned_to': managers[2], 'source': 'site_form'},
]

for d in leads_data:
    lead = Lead.objects.create(**d)
    LeadHistory.objects.create(lead=lead, action='created')

Lead.objects.filter(name__in=['Kamil Abdullaev', 'Saida Alieva']).update(
    created_at=timezone.now() - timedelta(days=5)
)

rasul = Lead.objects.get(phone='+79283456789')
LeadHistory.objects.create(lead=rasul, manager=managers[1], action='assigned')
LeadHistory.objects.create(lead=rasul, manager=managers[1], action='status_changed', from_status='assigned', to_status='in_work')
LeadHistory.objects.create(lead=rasul, manager=managers[1], action='comment', comment='2-room apt, budget 6M')

ibr = Lead.objects.get(phone='+79285678901')
for from_s, to_s in [('assigned','in_work'), ('in_work','meeting'), ('meeting','deal')]:
    LeadHistory.objects.create(lead=ibr, manager=managers[2], action='status_changed', from_status=from_s, to_status=to_s)
