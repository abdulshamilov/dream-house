"""
Мигрирует существующие цены карточек в InstallmentPlan(is_cash=True).

Запуск:
    python manage.py migrate_installment_data --dry-run   # проверка без записи
    python manage.py migrate_installment_data             # применить
"""
from django.core.management.base import BaseCommand

from cards.models import Card, InstallmentPlan


class Command(BaseCommand):
    help = 'Создаёт тарифы рассрочки (наличные) для карточек без плана'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано, не сохраняя в БД',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN — изменения не сохраняются ==='))

        cards = Card.objects.all().order_by('id')
        created = 0
        skipped = 0

        for card in cards:
            if InstallmentPlan.objects.filter(card=card, is_cash=True).exists():
                self.stdout.write(f'  ЕСТЬ    [{card.id}] {card.title!r} — наличный план уже существует')
                skipped += 1
                continue

            self.stdout.write(
                f'  СОЗДАТЬ [{card.id}] {card.title!r} — цена {card.price} ₽'
            )

            if not dry_run:
                InstallmentPlan.objects.create(
                    card=card,
                    is_cash=True,
                    term_months=0,
                    is_active=True,
                )
            created += 1

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: будет создано {created}, пропущено {skipped}. '
                'Запустите без --dry-run для применения.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Готово: создано {created}, пропущено {skipped}.'
            ))
