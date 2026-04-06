from django.db import models


class Payment(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Ученик'
    )
    amount = models.DecimalField(
        'Сумма (сум)',
        max_digits=12,
        decimal_places=0
    )
    date = models.DateTimeField('Дата оплаты')
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-date']

    def __str__(self):
        return f'{self.student.name} — {self.amount:,.0f} сум'
