from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta

from dashboard.models import Department, Employee, HRMetric, Alert, Recommendation, EngagementSurvey

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Генерация тестовых HR-данных'

    def handle(self, *args, **kwargs):
        self.stdout.write('Генерация данных...')

        # Создаем отделы
        departments_data = [
            ('IT', 'ИТ-отдел'),
            ('HR', 'Управление персоналом'),
            ('SALES', 'Продажи'),
            ('MARKETING', 'Маркетинг'),
            ('FINANCE', 'Финансы'),
            ('PROD', 'Производство'),
        ]

        depts = []
        for code, name in departments_data:
            dept, _ = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'budget': random.randint(1000000, 5000000)}
            )
            depts.append(dept)

        # Создаем сотрудников
        positions = {
            'IT': ['Разработчик', 'DevOps', 'QA-инженер', 'Архитектор', 'Product Manager'],
            'HR': ['HR-менеджер', 'Рекрутер', 'HRBP', 'Тренер'],
            'SALES': ['Менеджер по продажам', 'Региональный менеджер', 'Sales Director'],
            'MARKETING': ['Маркетолог', 'SMM-менеджер', 'Контент-менеджер'],
            'FINANCE': ['Бухгалтер', 'Финансовый аналитик', 'CFO'],
            'PROD': ['Инженер', 'Технолог', 'Начальник смены'],
        }

        for dept in depts:
            for _ in range(random.randint(15, 40)):
                hire_date = timezone.now().date() - timedelta(days=random.randint(30, 1000))
                is_active = random.random() > 0.15  # 15% уволенных

                emp = Employee.objects.create(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    department=dept,
                    position=random.choice(positions[dept.code]),
                    salary=random.randint(60000, 250000),
                    hire_date=hire_date,
                    birth_date=timezone.now().date() - timedelta(days=random.randint(6570, 21900)),
                    gender=random.choice(['M', 'F']),
                    is_active=is_active,
                    engagement_score=random.randint(50, 95),
                    performance_rating=random.randint(2, 5),
                    satisfaction_score=random.randint(45, 90),
                )

                if not is_active:
                    emp.exit_date = hire_date + timedelta(days=random.randint(100, 500))
                    emp.exit_reason = random.choice([
                        'Карьерный рост в другой компании',
                        'Низкая зарплата',
                        'Проблемы с руководством',
                        'Личные причины',
                        'Релокация'
                    ])
                    emp.save()

        # Создаем метрики
        for i in range(6):
            date = timezone.now().date() - timedelta(days=30 * i)
            for dept in depts:
                HRMetric.objects.create(
                    name=f'Текучесть {dept.name}',
                    metric_type='turnover',
                    value=random.uniform(5, 15),
                    target=8.0,
                    date_recorded=date,
                    department=dept,
                    trend=random.choice(['up', 'down', 'stable'])
                )

        # Создаем алерты
        alert_templates = [
            ('Высокая текучесть в IT-отделе', 'Текучесть превысила 15%', 'high'),
            ('Низкая вовлеченность в Продажах', 'Средний score ниже 60', 'medium'),
            ('Риск ухода ключевых сотрудников', '3 топ-перформера не получили повышение > 2 лет', 'critical'),
            ('Просроченные performance review', '15 сотрудников без оценки > 6 месяцев', 'medium'),
            ('Недобор в HR-отделе', 'Вакансии открыты > 90 дней', 'low'),
        ]

        for title, desc, severity in alert_templates:
            Alert.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'severity': severity,
                    'is_resolved': False
                }
            )

        # Создаем рекомендации
        recommendations = [
            {
                'title': 'Внедрить программу наставничества в IT',
                'desc': 'Снизить текучесть младших разработчиков через парное обучение',
                'priority': 'high',
                'impact': 'Снижение текучести на 20%',
                'cost': '150 000 ₽',
                'timeframe': '3 месяца'
            },
            {
                'title': 'Пересмотрить систему бонусов в Продажах',
                'desc': 'Внедрить KPI по удержанию клиентов в дополнение к новым продажам',
                'priority': 'high',
                'impact': 'Рост LTV на 15%',
                'cost': 'Без доп. затрат',
                'timeframe': '1 месяц'
            },
            {
                'title': 'Запустить pulse-опросы вовлеченности',
                'desc': 'Еженедельные 2-вопросные опросы для раннего выявления проблем',
                'priority': 'medium',
                'impact': 'Рост вовлеченности на 10%',
                'cost': '50 000 ₽',
                'timeframe': '2 недели'
            },
        ]

        for rec in recommendations:
            Recommendation.objects.get_or_create(
                title=rec['title'],
                defaults={
                    'description': rec['desc'],
                    'priority': rec['priority'],
                    'expected_impact': rec['impact'],
                    'implementation_cost': rec['cost'],
                    'timeframe': rec['timeframe']
                }
            )

        # Опрос вовлеченности
        EngagementSurvey.objects.get_or_create(
            title='Ежегодный опрос 2024',
            defaults={
                'date_conducted': timezone.now().date() - timedelta(days=30),
                'total_respondents': 120,
                'response_rate': 85,
                'overall_score': 72,
                'e_nps': 25,
                'satisfaction_work': 75,
                'satisfaction_management': 65,
                'satisfaction_career': 58,
                'satisfaction_compensation': 60,
                'satisfaction_worklife': 70,
            }
        )

        self.stdout.write(self.style.SUCCESS('Данные успешно сгенерированы!'))