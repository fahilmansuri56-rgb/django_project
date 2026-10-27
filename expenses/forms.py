from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Expense, Budget, Category

class ExpenseForm(forms.ModelForm):
    """
    ModelForm to easily create and update Expense objects.
    Widgets add CSS classes for modern styling.
    """
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'payment_method', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Grocery Shopping, Metro Recharge',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '₹ 0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Optional details or notes...'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class BudgetForm(forms.ModelForm):
    """
    Form to set or update monthly budget.
    """
    class Meta:
        model = Budget
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter monthly budget (₹)',
                'min': '100',
                'step': '100'
            })
        }


class RegisterForm(UserCreationForm):
    """
    User registration form with email field.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@example.com'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
