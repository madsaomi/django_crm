from django import forms
from .models import Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'phone', 'specialization']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО учителя'}),
            'phone': forms.TextInput(attrs={'class': 'form-control mask-phone', 'placeholder': '+998 XX XXX XX XX'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: General English', 'list': 'teacher_spec_list'}),
        }
