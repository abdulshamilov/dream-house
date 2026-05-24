import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_local')
django.setup()

from django.utils import timezone
from users.models import User
from developers.models import Developer
from cards.models import Card
from crm.models import Lead, Manager, LeadHistory

owner = User.objects.first()

# --- Developers ---
devs = []
for name, phone in [
    ('StrojGroup', '+7(8722)300001'),
    ('MakhStroy', '+7(8722)300002'),
    ('KaspijInvest', '+7(8722)300003'),
]:
    d, _ = Developer.objects.get_or_create(name=name, defaults={'phone': phone})
    devs.append(d)

# --- Cards ---
cards_cfg = [
    ('JK Pribrezhnyj', 'ul. Naberezhnaja, 12', 4500000, 65.0, 2, 1, 'residential', 'monolith', 'flat'),
    ('JK Solnechnyj',  'pr. Akushinskogo, 55', 3200000, 45.0, 1, 1, 'residential', 'brick',   'flat'),
    ('JK Kaspij',      'ul. Gamidova, 3',      7800000,110.0, 3, 2, 'residential', 'solid_monolith', 'flat'),
    ('JK Gornyj',      'ul. Lenina, 88',       2900000, 38.0, 1, 3, 'residential', 'panel',   'flat'),
    ('Apart Bujnaksk', 'ul. Sovetskaja, 14',   5100000, 72.0, 2, 1, 'apart',       'brick_monolith','flat'),
    ('JK Derbent Plaza','ul. Tagi-Zade, 7',    6300000, 90.0, 3, 3, 'residential', 'monolith','new_building'),
]
for title, address, price, area, rooms, city, ctype, htype, cat in cards_cfg:
    dev = devs[city % len(devs)]
    Card.objects.get_or_create(
        title=title,
        defaults=dict(
            owner=owner, developer=dev, address=address,
            description='Modern complex, great location.',
            price=price, area=area, rooms=rooms, city=city,
            complex_type=ctype, house_type=htype, category=cat,
            floors_total=12, elevator='cargo_passenger', parking='underground',
            balcony=True, finishing='with_finish', ceiling_height=2.85,
        )
    )
print('Cards:', Card.objects.count())

# --- Managers ---
mgrs = []
for name, tg_id, uname, is_admin in [
    ('Alibek Magomedov', 100000001, 'alibek_m',  True),
    ('Patimat Gadzhieva',100000002, 'patimat_g', False),
    ('Rasul Isaev',      100000003, 'rasul_i',   False),
]:
    m, _ = Manager.objects.get_or_create(
        telegram_id=tg_id,
        defaults={'name': name, 'telegram_username': uname, 'is_admin': is_admin}
    )
    mgrs.append(m)
print('Managers:', Manager.objects.count())

# --- Leads ---
leads_cfg = [
    ('Magomed Aliev',       '+79281001001', 'JK Pribrezhnyj'),
    ('Zarema Khasanova',    '+79281001002', 'JK Solnechnyj'),
    ('Ibragim Murtazaliev', '+79281001003', 'JK Kaspij'),
    ('Aminat Dzhabrailova', '+79281001004', 'JK Gornyj'),
    ('Shamil Gusaev',       '+79281001005', 'Apart Bujnaksk'),
    ('Khadizhat Omarova',   '+79281001006', 'JK Derbent Plaza'),
    ('Rustam Kadiev',       '+79281001007', 'JK Pribrezhnyj'),
    ('Saida Nurmagomedova', '+79281001008', 'JK Solnechnyj'),
    ('Arsen Temirkhanov',   '+79281001009', 'JK Kaspij'),
    ('Kamila Abdulaeva',    '+79281001010', 'JK Gornyj'),
]
statuses = ['new', 'assigned', 'in_work', 'meeting', 'deal', 'rejected']

for i, (name, phone, jk) in enumerate(leads_cfg):
    if Lead.objects.filter(phone=phone).exists():
        continue
    st = statuses[i % len(statuses)]
    mgr = mgrs[i % 2 + 1] if st != 'new' else None
    lead = Lead.objects.create(
        name=name, phone=phone, jk=jk, status=st,
        assigned_to=mgr,
        source='site_form',
        raw_data={'utm': 'google', 'page': f'/jk/{i+1}'},
        assigned_at=timezone.now() if mgr else None,
        closed_at=timezone.now() if st in ('deal', 'rejected') else None,
    )
    LeadHistory.objects.create(lead=lead, action='created')
    if mgr:
        LeadHistory.objects.create(lead=lead, manager=mgrs[0], action='assigned')
    if st in ('in_work', 'meeting', 'deal', 'rejected'):
        LeadHistory.objects.create(
            lead=lead, manager=mgr, action='status_changed',
            from_status='assigned', to_status=st,
        )
    if i % 3 == 0:
        LeadHistory.objects.create(
            lead=lead, manager=mgr, action='comment',
            comment='Client will call back after 18:00',
        )

print('Leads:', Lead.objects.count())
print('Done!')
