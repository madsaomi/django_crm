from django import forms
from .models import Material, ProgressTest

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'material_type', 'file', 'url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название (например: Таблица неправильных глаголов)'}),
            'material_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

class ProgressTestForm(forms.ModelForm):
    class Meta:
        model = ProgressTest
        fields = ['title', 'date', 'max_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Final Test'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
