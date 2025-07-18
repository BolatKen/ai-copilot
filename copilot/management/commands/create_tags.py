from django.core.management.base import BaseCommand
from copilot.models import Tag

class Command(BaseCommand):
    help = 'Создает базовые теги для модерации контента'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить все существующие теги перед созданием новых',
        )

    def handle(self, *args, **options):
        if options['reset']:
            Tag.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Все существующие теги удалены')
            )
        
        dangerous_tags = [
            'pornography',
            'violence', 
            'profanity',
            'dangerous_symbols',
            'hate_speech',
            'weapons',
            'drugs',
            'self_harm',
            'extremism',
            'nudity',
            'blood',
            'gore',
            'terrorism',
            'nazi_symbols',
            'racist_content',
            'sexual_content',
            'disturbing_content',
            'graphic_violence',
            'suicide',
            'abuse'
        ]
        
        created_count = 0
        for tag_name in dangerous_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1
                self.stdout.write(f'Создан тег: {tag_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Команда выполнена успешно! Создано {created_count} новых тегов из {len(dangerous_tags)} возможных.'
            )
        )

