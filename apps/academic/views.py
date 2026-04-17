from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.groups.models import Group
from apps.students.models import Student
from .models import ProgressTest, TestResult
from .forms import MaterialForm, ProgressTestForm
from datetime import date

@login_required
def add_material(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.group = group
            material.save()
            messages.success(request, 'Материал успешно добавлен.')
            return redirect('groups:detail', pk=group_id)
    else:
        form = MaterialForm()
    
    return render(request, 'academic/add_material_modal.html', {
        'form': form,
        'group': group
    })

@login_required
def conduct_test(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    students = [e.student for e in group.enrollments.filter(is_active=True).select_related('student')]
    
    if request.method == 'POST':
        form = ProgressTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.group = group
            test.save()
            
            # Сохранение оценок из POST
            for student in students:
                score_str = request.POST.get(f'score_{student.id}')
                score = int(score_str) if score_str and score_str.isdigit() else 0
                score = min(score, test.max_score) # Ограничиваем максимальным баллом
                TestResult.objects.create(
                    test=test,
                    student=student,
                    score=score
                )
                
            messages.success(request, f'Тест «{test.title}» успешно сохранен.')
            return redirect('groups:detail', pk=group_id)
    else:
        form = ProgressTestForm(initial={'max_score': 100, 'date': date.today()})
        
    return render(request, 'academic/conduct_test.html', {
        'form': form,
        'group': group,
        'students': students
    })
