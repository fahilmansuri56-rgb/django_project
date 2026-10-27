from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

from .models import Expense, Category, Budget
from .forms import ExpenseForm, BudgetForm, RegisterForm


def register_view(request):
    """
    User registration view.
    Creates a new user and logs them in immediately.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to ExpenseTracker, {user.username}! Your account is ready.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """
    User login view with validation.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Main dashboard displaying:
    1. Total lifetime spend
    2. Current month spend
    3. Monthly budget vs actual spending with progress
    4. Category-wise expense breakdown
    5. Recent 5 expenses
    """
    user = request.user
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # 1. All expenses for user
    user_expenses = Expense.objects.filter(user=user)

    # 2. Total lifetime expenses
    total_spent = user_expenses.aggregate(total=Sum('amount'))['total'] or 0

    # 3. Current month expenses
    current_month_expenses = user_expenses.filter(date__year=current_year, date__month=current_month)
    month_spent = current_month_expenses.aggregate(total=Sum('amount'))['total'] or 0

    # 4. Monthly Budget
    budget_obj, created = Budget.objects.get_or_create(
        user=user,
        month=current_month,
        year=current_year,
        defaults={'amount': 15000.00}
    )
    budget_amount = budget_obj.amount
    remaining_budget = max(0, budget_amount - month_spent)
    budget_percentage = min(100, int((month_spent / budget_amount) * 100)) if budget_amount > 0 else 0

    # 5. Recent 5 transactions
    recent_expenses = user_expenses[:5]

    # 6. Category breakdown for current month (or all-time if no expenses this month)
    category_summary = (
        (current_month_expenses if current_month_expenses.exists() else user_expenses)
        .values('category__name', 'category__icon', 'category__color')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    context = {
        'total_spent': total_spent,
        'month_spent': month_spent,
        'budget_amount': budget_amount,
        'remaining_budget': remaining_budget,
        'budget_percentage': budget_percentage,
        'recent_expenses': recent_expenses,
        'category_summary': category_summary,
        'current_month_name': now.strftime('%B %Y'),
        'budget_form': BudgetForm(instance=budget_obj),
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def expense_list_view(request):
    """
    List all expenses with live search and filtering:
    - Search by keyword
    - Filter by category
    - Filter by date range (from_date to to_date)
    """
    expenses = Expense.objects.filter(user=request.user)
    categories = Category.objects.all()

    # Filter by search keyword
    q = request.GET.get('q', '').strip()
    if q:
        expenses = expenses.filter(title__icontains=q)

    # Filter by category
    category_id = request.GET.get('category', '').strip()
    if category_id:
        expenses = expenses.filter(category_id=category_id)

    # Filter by start date
    from_date = request.GET.get('from_date', '').strip()
    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    # Filter by end date
    to_date = request.GET.get('to_date', '').strip()
    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    # Calculate total for current filtered view
    filtered_total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'categories': categories,
        'filtered_total': filtered_total,
        'search_query': q,
        'selected_category': category_id,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def add_expense_view(request):
    """
    Create a new expense entry linked to the logged-in user.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f"Expense '{expense.title}' of ₹{expense.amount} added successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'action_title': 'Add New Expense',
        'button_text': 'Save Expense'
    })


@login_required
def edit_expense_view(request, pk):
    """
    Edit an existing expense.
    Security: get_object_or_404 with user=request.user ensures users can only edit their own records.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f"Expense '{expense.title}' updated successfully!")
            return redirect('expense_list')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'expense': expense,
        'action_title': f"Edit Expense: {expense.title}",
        'button_text': 'Update Expense'
    })


@login_required
def delete_expense_view(request, pk):
    """
    Delete an expense entry.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        title = expense.title
        amount = expense.amount
        expense.delete()
        messages.success(request, f"Expense '{title}' (₹{amount}) deleted successfully.")
        return redirect('expense_list')

    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def update_budget_view(request):
    """
    Update monthly budget for current month.
    """
    if request.method == 'POST':
        now = timezone.now()
        budget_obj, _ = Budget.objects.get_or_create(
            user=request.user,
            month=now.month,
            year=now.year
        )
        form = BudgetForm(request.POST, instance=budget_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Monthly budget updated to ₹{budget_obj.amount}!")
        else:
            messages.error(request, "Invalid budget amount.")

    return redirect('dashboard')


@login_required
def chart_data_api(request):
    """
    API endpoint returning JSON data for Chart.js.
    Shows Category-wise spend breakdown for the logged-in user.
    """
    user_expenses = Expense.objects.filter(user=request.user)

    # Category breakdown
    data = (
        user_expenses.values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    labels = []
    values = []
    colors = []

    for item in data:
        cat_name = item['category__name'] or 'Uncategorized'
        labels.append(cat_name)
        values.append(float(item['total'] or 0))
        colors.append(item['category__color'] or '#6B7280')

    return JsonResponse({
        'labels': labels,
        'data': values,
        'colors': colors,
        'has_data': len(values) > 0
    })
