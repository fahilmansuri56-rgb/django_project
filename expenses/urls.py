from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Analytics
    path('', views.dashboard_view, name='dashboard'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),

    # Expense CRUD
    path('expenses/', views.expense_list_view, name='expense_list'),
    path('expenses/add/', views.add_expense_view, name='add_expense'),
    path('expenses/<int:pk>/edit/', views.edit_expense_view, name='edit_expense'),
    path('expenses/<int:pk>/delete/', views.delete_expense_view, name='delete_expense'),

    # Budget
    path('budget/update/', views.update_budget_view, name='update_budget'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
