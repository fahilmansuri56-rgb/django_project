from django.core.management.base import BaseCommand
from expenses.models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Food & Dining', 'icon': '🍔', 'color': '#EF4444'},
    {'name': 'Shopping', 'icon': '🛍️', 'color': '#F59E0B'},
    {'name': 'Transportation', 'icon': '🚗', 'color': '#3B82F6'},
    {'name': 'Entertainment', 'icon': '🎬', 'color': '#8B5CF6'},
    {'name': 'Bills & Utilities', 'icon': '💡', 'color': '#10B981'},
    {'name': 'Health & Fitness', 'icon': '💊', 'color': '#EC4899'},
    {'name': 'Education', 'icon': '📚', 'color': '#06B6D4'},
    {'name': 'Others', 'icon': '📦', 'color': '#6B7280'},
]

class Command(BaseCommand):
    help = 'Seed default expense categories'

    def handle(self, *args, **options):
        created_count = 0
        for cat in DEFAULT_CATEGORIES:
            obj, created = Category.objects.get_or_create(
                name=cat['name'],
                defaults={'icon': cat['icon'], 'color': cat['color']}
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully initialized categories! ({created_count} new)'))
