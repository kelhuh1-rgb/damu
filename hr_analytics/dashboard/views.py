from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Employee, Department, HRMetric
from .forms import (
    CustomLoginForm, CustomUserCreationForm, UserUpdateForm,
    ProfileUpdateForm, CustomPasswordChangeForm
)
from datetime import datetime, timedelta
import json


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        messages.success(self.request,
                         f'Добро пожаловать, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем профиль сотрудника данными из формы
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()

            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    employee = request.user.employee_profile
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.employee_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.employee_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'edit_profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})


@login_required
def dashboard(request):
    # Основные KPI
    total_employees = Employee.objects.filter(is_active=True).count()
    avg_performance = Employee.objects.filter(is_active=True).aggregate(Avg('performance_score'))[
                          'performance_score__avg'] or 0
    avg_engagement = Employee.objects.filter(is_active=True).aggregate(Avg('engagement_score'))[
                         'engagement_score__avg'] or 0

    # Текучесть кадров
    thirty_days_ago = datetime.now() - timedelta(days=30)
    turnover_rate = 5.2

    # Данные по отделам
    departments = Department.objects.all()
    dept_data = []
    for dept in departments:
        emp_count = Employee.objects.filter(department=dept, is_active=True).count()
        avg_perf = Employee.objects.filter(department=dept, is_active=True).aggregate(Avg('performance_score'))[
                       'performance_score__avg'] or 0
        dept_data.append({
            'name': dept.name,
            'count': emp_count,
            'avg_performance': round(avg_perf, 1)
        })

    # Данные для графиков
    chart_data = {
        'departments': [d['name'] for d in dept_data],
        'employee_counts': [d['count'] for d in dept_data],
        'performance_scores': [d['avg_performance'] for d in dept_data],
    }

    context = {
        'total_employees': total_employees,
        'avg_performance': round(avg_performance, 1),
        'avg_engagement': round(avg_engagement, 1),
        'turnover_rate': turnover_rate,
        'departments': dept_data,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'index.html', context)


@login_required
def analytics(request):
    metrics = HRMetric.objects.all().order_by('-date_recorded')[:50]

    # Тренды по месяцам
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн']
    turnover_trend = [4.2, 4.5, 5.1, 4.8, 5.2, 5.0]
    engagement_trend = [72, 74, 71, 76, 78, 80]

    context = {
        'metrics': metrics,
        'months': json.dumps(months),
        'turnover_trend': json.dumps(turnover_trend),
        'engagement_trend': json.dumps(engagement_trend),
    }
    return render(request, 'analytics.html', context)


@login_required
def api_metrics(request):
    data = {
        'employees_by_dept': list(Employee.objects.values('department__name').annotate(count=Count('id'))),
        'avg_metrics': {
            'performance': Employee.objects.filter(is_active=True).aggregate(Avg('performance_score'))[
                'performance_score__avg'],
            'engagement': Employee.objects.filter(is_active=True).aggregate(Avg('engagement_score'))[
                'engagement_score__avg'],
        }
    }
    return JsonResponse(data)