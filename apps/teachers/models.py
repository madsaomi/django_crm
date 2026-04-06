from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    specialization = models.CharField('Специализация', max_length=100, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_active = models.BooleanField('Активный', default=True)
    class Meta:
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'
        ordering = ['name']

    def __str__(self):
        return self.name
