from django import forms
from .models import Payment
from django.utils import timezone


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'amount', 'date', 'comment']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 500000'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'comment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Комментарий', 'list': 'payment_comment_list'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
