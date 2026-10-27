from django.contrib import admin
from .models import Category, Expense, Budget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'category', 'payment_method', 'date', 'created_at')
    list_filter = ('category', 'payment_method', 'date', 'user')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'amount')
    list_filter = ('month', 'year')
