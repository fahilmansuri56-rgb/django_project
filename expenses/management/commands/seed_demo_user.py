from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Category, Expense, Budget
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create demo user with realistic expenses for interview demonstration'

    def handle(self, *args, **options):
        # 1. Create or get demo user
        user, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com'})
        user.set_password('demo123')
        user.save()

        # Also create admin superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' with password 'admin123'"))

        # 2. Set monthly budget for demo user
        now = timezone.now()
        budget, _ = Budget.objects.get_or_create(
            user=user,
            month=now.month,
            year=now.year,
            defaults={'amount': 20000.00}
        )

        # 3. Create realistic sample expenses
        sample_expenses = [
            ('Grocery & Supermarket', 2450.00, 'Food & Dining', 'UPI', 1, 'Monthly pulses, vegetables, and milk'),
            ('Weekend Dining with Friends', 1200.00, 'Food & Dining', 'Card', 3, 'Dinner at Barbeque Nation'),
            ('Electricity & Internet Bill', 1850.00, 'Bills & Utilities', 'NetBanking', 5, 'Torrent Power & Fiber Broadband'),
            ('Fuel Petrol', 800.00, 'Transportation', 'UPI', 2, 'Bike tank refill'),
            ('New Formal Shoes', 2199.00, 'Shopping', 'Card', 6, 'For interview preparation'),
            ('Movie & Popcorn', 650.00, 'Entertainment', 'UPI', 8, 'Watched new movie at PVR'),
            ('Online Python & Web Course', 999.00, 'Education', 'UPI', 10, 'Certification on Udemy'),
            ('Medical Pharmacy', 340.00, 'Health & Fitness', 'Cash', 12, 'Vitamins and regular meds'),
            ('Mobile Postpaid Recharge', 499.00, 'Bills & Utilities', 'UPI', 15, 'Monthly 5G unlimited plan'),
            ('Office Commute Metro Pass', 600.00, 'Transportation', 'UPI', 4, 'Monthly metro smart card'),
        ]

        # Clear existing expenses for demo user so command is idempotent
        Expense.objects.filter(user=user).delete()

        today = timezone.now().date()
        for title, amount, cat_name, method, days_ago, desc in sample_expenses:
            cat = Category.objects.filter(name=cat_name).first()
            Expense.objects.create(
                user=user,
                title=title,
                amount=amount,
                category=cat,
                payment_method=method,
                date=today - timedelta(days=days_ago),
                description=desc
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo user ('demo' / 'demo123') with 10 sample expenses!"))
