from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CourseType(models.TextChoices):
    KIDS_ENGLISH = 'KIDS_ENGLISH', 'Kids English'
    GENERAL_ENGLISH = 'GENERAL_ENGLISH', 'General English'
    IELTS = 'IELTS', 'IELTS'
    MATH = 'MATH', 'Математика'
    SAT = 'SAT', 'SAT'


class ScheduleType(models.TextChoices):
    EVEN = 'EVEN', 'Чётные дни'
    ODD = 'ODD', 'Нечётные дни'

class GroupColor(models.TextChoices):
    EMERALD = 'bg-t-1', 'Изумрудный (Зеленый)'
    INDIGO = 'bg-t-2', 'Индиго (Сине-фиолетовый)'
    AMBER = 'bg-t-3', 'Янтарный (Оранжевый)'
    OCEAN = 'bg-t-4', 'Океан (Синий)'
    ROSE = 'bg-t-5', 'Роза (Красный)'
    SLATE = 'bg-t-6', 'Серый (Нейтральный)'


# Default pricing per course type (in soums)
COURSE_DEFAULT_PRICES = {
    'KIDS_ENGLISH': 400000,
    'GENERAL_ENGLISH': 450000,
    'IELTS': 600000,
    'MATH': 400000,
    'SAT': 400000,
}


class Group(models.Model):
    name = models.CharField('Название группы', max_length=200)
    course_type = models.CharField(
        'Тип курса',
        max_length=20,
        choices=CourseType.choices,
        default=CourseType.GENERAL_ENGLISH
    )
    level = models.CharField(
        'Уровень',
        max_length=100,
        blank=True,
        help_text='Для General English: Beginner, Elementary, Pre-Intermediate, Intermediate, Upper-Intermediate, Advanced'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups',
        verbose_name='Учитель'
    )
    schedule_type = models.CharField(
        'Расписание',
        max_length=4,
        choices=ScheduleType.choices,
        default=ScheduleType.EVEN
    )
    time_slot = models.CharField('Время', max_length=50, blank=True)
    room = models.CharField('Кабинет', max_length=50, blank=True)
    monthly_fee = models.DecimalField(
        'Ежемесячная оплата (сум)',
        max_digits=12,
        decimal_places=0,
        default=400000
    )
    max_students = models.PositiveIntegerField(
        'Макс. учеников',
        default=12,
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    duration_months = models.PositiveIntegerField(
        'Длительность уровня (мес.)',
        default=3,
        help_text='General English — 3 мес., IELTS скилл — 1 мес.'
    )
    color = models.CharField(
        'Цвет карточки',
        max_length=20,
        choices=GroupColor.choices,
        default=GroupColor.EMERALD
    )
    is_active = models.BooleanField('Активная', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_course_type_display()})'

    @property
    def students_count(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def is_full(self):
        return self.students_count >= self.max_students

    @property
    def available_spots(self):
        return max(0, self.max_students - self.students_count)


class Enrollment(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Ученик'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Группа'
    )
    enrolled_date = models.DateField('Дата зачисления', auto_now_add=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Зачисление'
        verbose_name_plural = 'Зачисления'
        unique_together = ['student', 'group']
        ordering = ['-enrolled_date']

    def __str__(self):
        return f'{self.student.name} → {self.group.name}'


class SundayEvent(models.Model):
    title = models.CharField('Название', max_length=200)
    date = models.DateField('Дата')
    time_slot = models.CharField('Время', max_length=50)
    room = models.CharField('Кабинет', max_length=50)
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Учитель'
    )
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Воскресный ивент'
        verbose_name_plural = 'Воскресные ивенты'
        ordering = ['date', 'time_slot']

    def __str__(self):
        return f'{self.title} ({self.date})'
