from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class MaterialType(models.TextChoices):
    FILE = 'FILE', 'Файл'
    LINK = 'LINK', 'Ссылка'

class Material(models.Model):
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='materials', verbose_name='Группа')
    title = models.CharField('Название', max_length=200)
    material_type = models.CharField('Тип материала', max_length=4, choices=MaterialType.choices, default=MaterialType.LINK)
    file = models.FileField('Файл', upload_to='materials/', null=True, blank=True)
    url = models.URLField('Ссылка', null=True, blank=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.get_material_type_display()})"

class ProgressTest(models.Model):
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='tests', verbose_name='Группа')
    title = models.CharField('Название теста', max_length=200)
    date = models.DateField('Дата проведения')
    max_score = models.PositiveIntegerField('Максимальный балл', default=100)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Срезовый тест'
        verbose_name_plural = 'Срезовые тесты'
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.title} - {self.group.name}"

class TestResult(models.Model):
    test = models.ForeignKey(ProgressTest, on_delete=models.CASCADE, related_name='results', verbose_name='Тест')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='test_results', verbose_name='Ученик')
    score = models.PositiveIntegerField('Балл', default=0)
    
    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'
        unique_together = ['test', 'student']
        ordering = ['-test__date', 'student__name']
        
    def __str__(self):
        return f"{self.student.name}: {self.score}/{self.test.max_score}"
    
    @property
    def percentage(self):
        if self.test.max_score > 0:
            return round((self.score / self.test.max_score) * 100)
        return 0
