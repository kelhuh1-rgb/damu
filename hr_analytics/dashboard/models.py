from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название отдела')
    manager = models.CharField(max_length=100, verbose_name='Руководитель')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile',
                                verbose_name='Пользователь')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Отдел')
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    bio = models.TextField(blank=True, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')

    # HR метрики
    hire_date = models.DateField(auto_now_add=True, verbose_name='Дата приёма')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Зарплата')
    performance_score = models.FloatField(default=0, verbose_name='Оценка производительности')
    engagement_score = models.FloatField(default=0, verbose_name='Вовлечённость')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return f'{self.user.get_full_name()}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class HRMetric(models.Model):
    METRIC_TYPES = [
        ('turnover', 'Текучесть кадров'),
        ('engagement', 'Вовлечённость'),
        ('performance', 'Производительность'),
        ('satisfaction', 'Удовлетворённость'),
        ('absence', 'Пропуски'),
    ]

    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name='Тип метрики')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Отдел')
    value = models.FloatField(verbose_name='Значение')
    date_recorded = models.DateField(verbose_name='Дата записи')
    target_value = models.FloatField(default=0, verbose_name='Целевое значение')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Записал')

    def __str__(self):
        return f'{self.get_metric_type_display()} - {self.department.name}'

    class Meta:
        verbose_name = 'HR-метрика'
        verbose_name_plural = 'HR-метрики'


# Автоматическое создание профиля при регистрации
@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_employee_profile(sender, instance, **kwargs):
    if hasattr(instance, 'employee_profile'):
        instance.employee_profile.save()