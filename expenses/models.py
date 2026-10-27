from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """
    Category model for grouping expenses (e.g., Food, Travel, Bills).
    """
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=30, default='🏷️', help_text="Emoji or Icon symbol")
    color = models.CharField(max_length=20, default='#3B82F6', help_text="Hex color code for charts")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"


class Expense(models.Model):
    """
    Core Expense model tracking individual spending entries for each user.
    """
    PAYMENT_CHOICES = [
        ('UPI', 'UPI / Online Payment'),
        ('Cash', 'Cash'),
        ('Card', 'Debit / Credit Card'),
        ('NetBanking', 'Net Banking'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='expenses')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UPI')
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.user.username})"


class Budget(models.Model):
    """
    Monthly spending budget per user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.PositiveSmallIntegerField(default=timezone.now().month)
    year = models.PositiveSmallIntegerField(default=timezone.now().year)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

    class Meta:
        unique_together = ('user', 'month', 'year')

    def __str__(self):
        return f"{self.user.username}'s Budget ({self.month}/{self.year}) - ₹{self.amount}"
