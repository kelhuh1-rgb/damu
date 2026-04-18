from django.contrib import admin
from .models import Employee, Department, HRMetric
from django.utils.safestring import mark_safe

# =======================
# Department Admin
# =======================
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'get_employee_count']
    search_fields = ['name', 'manager']
    list_filter = ['name']

    def get_employee_count(self, obj):
        return obj.employee_set.count()
    get_employee_count.short_description = 'Сотрудников'


# =======================
# Employee Admin
# =======================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'get_avatar',
        'get_full_name',
        'department',
        'position',
        'salary',
        'performance_score',
        'engagement_score',
        'is_active'
    ]

    list_filter = [
        'department',
        'is_active',
        'hire_date'
    ]

    search_fields = [
        'user__first_name',
        'user__last_name',
        'position'
    ]

    list_editable = [
        'position',
        'salary',
        'performance_score',
        'engagement_score',
        'is_active'
    ]

    readonly_fields = ['hire_date', 'get_avatar_preview']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'department', 'position')
        }),
        ('Контакты', {
            'fields': ('phone', 'bio')
        }),
        ('Аватар', {
            'fields': ('avatar', 'get_avatar_preview')
        }),
        ('HR Метрики', {
            'fields': ('salary', 'performance_score', 'engagement_score', 'is_active')
        }),
        ('Даты', {
            'fields': ('hire_date', 'birth_date')
        }),
    )

    # =======================
    # Кастомные методы
    # =======================

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'ФИО'

    def get_avatar(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="40" height="40" style="border-radius:50%;" />'
        return '—'
    get_avatar.allow_tags = True
    get_avatar.short_description = 'Фото'

    def get_avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="100" />'
        return 'Нет аватара'
    get_avatar_preview.allow_tags = True
    get_avatar_preview.short_description = 'Превью'


# =======================
# HR Metrics Admin
# =======================
@admin.register(HRMetric)
class HRMetricAdmin(admin.ModelAdmin):
    list_display = [
        'metric_type',
        'department',
        'value',
        'target_value',
        'date_recorded',
        'recorded_by'
    ]

    list_filter = [
        'metric_type',
        'department',
        'date_recorded'
    ]

    search_fields = [
        'department__name',
        'metric_type'
    ]

    date_hierarchy = 'date_recorded'

    ordering = ['-date_recorded']