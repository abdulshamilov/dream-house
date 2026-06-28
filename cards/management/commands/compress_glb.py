import shutil
import subprocess
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from cards.models import Card


class Command(BaseCommand):
    """Сжимает .glb файл карточки с помощью gltf-transform draco и заменяет оригинал."""

    help = 'Сжимает 3D-модель (.glb) карточки через gltf-transform draco'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            'apartment_id',
            type=int,
            help='ID карточки (Card)',
        )

    def handle(self, *args, **options) -> None:
        card_id: int = options['apartment_id']

        if not shutil.which('gltf-transform'):
            raise CommandError(
                'gltf-transform не найден в PATH.\n'
                'Установите: npm install -g @gltf-transform/cli'
            )

        try:
            card = Card.objects.get(pk=card_id)
        except Card.DoesNotExist:
            raise CommandError(f'Карточка с ID {card_id} не найдена.')

        if not card.model_3d_glb:
            raise CommandError(f'У карточки {card_id} нет загруженной 3D-модели (.glb).')

        original_path = Path(card.model_3d_glb.path)
        if not original_path.exists():
            raise CommandError(f'Файл не найден на диске: {original_path}')

        tmp_fd, tmp_name = tempfile.mkstemp(suffix='.glb')
        tmp_path = Path(tmp_name)
        try:
            import os
            os.close(tmp_fd)

            self.stdout.write(f'Исходный файл: {original_path}')
            self.stdout.write(f'Размер до: {original_path.stat().st_size // 1024} КБ')

            result = subprocess.run(
                ['gltf-transform', 'draco', str(original_path), str(tmp_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise CommandError(
                    f'gltf-transform завершился с ошибкой (код {result.returncode}):\n'
                    f'{result.stderr.strip()}'
                )

            original_size = original_path.stat().st_size
            compressed_size = tmp_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100 if original_size else 0

            tmp_path.replace(original_path)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Готово! {original_size // 1024} КБ → {compressed_size // 1024} КБ '
                    f'(сжатие {ratio:.1f}%)'
                )
            )
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(str(exc)) from exc
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
