from django import forms
from .models import Group, Enrollment, COURSE_DEFAULT_PRICES, SundayEvent


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'course_type', 'level', 'teacher', 'schedule_type', 'time_slot',
                  'room', 'color', 'monthly_fee', 'max_students', 'duration_months', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: IELTS Foundation', 'list': 'teacher_spec_list'}),
            'course_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_course_type'}),
            'level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Beginner, Elementary...', 'list': 'level_list'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'schedule_type': forms.Select(attrs={'class': 'form-select'}),
            'time_slot': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 14:00 - 15:30', 'list': 'time_slot_list'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер кабинета', 'list': 'room_list'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 500000'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 12'}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 6'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'group']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
        }


class AddStudentToGroupForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=None,
        label='Ученик',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.students.models import Student
        if group:
            enrolled_ids = group.enrollments.values_list('student_id', flat=True)
            self.fields['student'].queryset = Student.objects.filter(
                is_active=True
            ).exclude(id__in=enrolled_ids)
        else:
            self.fields['student'].queryset = Student.objects.filter(is_active=True)


class SundayEventForm(forms.ModelForm):
    class Meta:
        model = SundayEvent
        fields = ['title', 'date', 'time_slot', 'room', 'teacher', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название ивента', 'list': 'teacher_spec_list'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 10:00 - 12:00', 'list': 'time_slot_list'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер кабинета', 'list': 'room_list'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание'}),
        }
