from django import forms
from .models import Manager


class ManagerForm(forms.ModelForm):
    class Meta:
        model = Manager
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО менеджера'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 XX XXX XX XX'}),
        }
