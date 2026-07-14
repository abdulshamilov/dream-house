"""
Массовый импорт тарифов рассрочки из текстового файла.

Формат файла — блоками по ЖК:

    [Новый Горизонт 10 блок]        # подстрока названия карточки
    нал 75000 2-8
    300к 90000 55 2-8
    500к 85000 55 2-8

    [id:42, id:43]                  # либо явные id карточек
    30% 100000 36

Внутри блока — тот же синтаксис, что в «быстром заполнении» админки:
    нал <цена>              — наличные (100% взнос)
    <взнос> <цена> <срок>   — фикс. взнос (300к, 500тыс, 1млн)
    <N>% <цена> <срок>      — процентный взнос
    ... [этажи]             — необязательный диапазон, например 2-8

Примеры:
    python manage.py import_installments docs/installments.txt --dry-run
    python manage.py import_installments docs/installments.txt --replace
"""
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cards.admin import parse_quick_fill
from cards.models import Card, InstallmentPlan


def parse_file(text):
    """Возвращает [(селектор, [строки тарифов]), ...]."""
    blocks = []
    selector, lines = None, []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            if selector is not None:
                blocks.append((selector, lines))
            selector, lines = line[1:-1].strip(), []
        elif selector is not None:
            lines.append(line)
    if selector is not None:
        blocks.append((selector, lines))
    return blocks


def resolve_cards(selector):
    """Селектор → queryset карточек. 'id:1, id:2' либо подстрока названия."""
    parts = [p.strip() for p in selector.split(',') if p.strip()]
    if all(p.lower().startswith('id:') for p in parts):
        ids = [int(p[3:]) for p in parts]
        return Card.objects.filter(pk__in=ids)
    return Card.objects.filter(title__icontains=selector)


class Command(BaseCommand):
    help = 'Импорт тарифов рассрочки из текстового файла'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Путь к файлу с условиями')
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Показать, что будет сделано, ничего не записывая',
        )
        parser.add_argument(
            '--replace', action='store_true',
            help='Удалить существующие тарифы у затронутых карточек перед импортом',
        )

    def handle(self, *args, **opts):
        try:
            with open(opts['path'], encoding='utf-8') as f:
                text = f.read()
        except OSError as e:
            raise CommandError(f'Не удалось открыть файл: {e}')

        blocks = parse_file(text)
        if not blocks:
            raise CommandError('В файле нет ни одного блока [ЖК]')

        created_total = 0
        problems = []

        with transaction.atomic():
            for selector, lines in blocks:
                cards = list(resolve_cards(selector))
                if not cards:
                    problems.append(f'НЕ НАЙДЕНО: [{selector}] — ни одной карточки')
                    continue

                try:
                    plans = parse_quick_fill('\n'.join(lines))
                except ValidationError as e:
                    problems.append(f'ОШИБКА в блоке [{selector}]: {e.messages[0]}')
                    continue

                self.stdout.write(
                    f'\n[{selector}] → карточек: {len(cards)}, тарифов на карточку: {len(plans)}'
                )
                for card in cards:
                    self.stdout.write(f'    #{card.pk} {card.title} ({card.area} м²)')

                if opts['dry_run']:
                    for p in plans:
                        self.stdout.write(f'      {self._describe(p)}')
                    continue

                for card in cards:
                    if opts['replace']:
                        InstallmentPlan.objects.filter(card=card).delete()
                    InstallmentPlan.objects.bulk_create([
                        InstallmentPlan(card=card, **p) for p in plans
                    ])
                    created_total += len(plans)

            if opts['dry_run']:
                transaction.set_rollback(True)

        for p in problems:
            self.stdout.write(self.style.WARNING(p))

        if opts['dry_run']:
            self.stdout.write(self.style.WARNING('\nDRY-RUN: ничего не записано'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nСоздано тарифов: {created_total}'))

    def _describe(self, p):
        if p['is_cash']:
            return f"наличные — {p['price_per_sqm']} ₽/м²{self._floors(p)}"
        if p.get('down_payment_type') == 'percent':
            down = f"взнос {p['down_payment_percent']}%"
        else:
            down = f"взнос от {p['down_payment_min_amount']} ₽"
            if p.get('down_payment_max_amount'):
                down += f" до {p['down_payment_max_amount']} ₽"
        return f"{down} — {p['price_per_sqm']} ₽/м², {p['term_months']} мес.{self._floors(p)}"

    def _floors(self, p):
        if p['floor_from'] and p['floor_to']:
            return f" [{p['floor_from']}-{p['floor_to']} эт.]"
        return ''
