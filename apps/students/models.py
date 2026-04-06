from django.db import models


class Student(models.Model):
    name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    manager = models.ForeignKey(
        'managers.Manager',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='Менеджер'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_active = models.BooleanField('Активный', default=True)

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'
        ordering = ['name']

    def __str__(self):
        return self.name
