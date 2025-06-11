from django.core.management.base import BaseCommand
from copilot.models import Tag

class Command(BaseCommand):
    help = 'Создает базовые теги для модерации контента'

    def handle(self, *args, **options):
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
            'racist_content'
        ]
        
        created_count = 0
        for tag_name in dangerous_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1
                self.stdout.write(f'Создан тег: {tag_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} новых тегов')
        )

