from django.db import models


class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Присутствует'
    ABSENT = 'ABSENT', 'Отсутствует'


class Attendance(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Ученик'
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Группа'
    )
    date = models.DateField('Дата')
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    grade = models.CharField('Оценка', max_length=5, blank=True, null=True)
    comment = models.CharField('Комментарий', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        unique_together = ['student', 'group', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.student.name} — {self.date} — {self.get_status_display()}'
