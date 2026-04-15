import re
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.students.models import Student
from apps.groups.models import Group
from apps.teachers.models import Teacher

@login_required
def global_search(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return render(request, 'components/search_results.html', {'results': []})
        
    def highlight(text, query):
        if not query: return text
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f'<span class="text-primary">{m.group(0)}</span>', str(text))
        
    students = Student.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))[:5]
    groups = Group.objects.filter(Q(name__icontains=q) | Q(course_type__icontains=q))[:5]
    teachers = Teacher.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))[:5]
    
    results = []
    
    for s in students:
        results.append({
            'title': highlight(s.name, q),
            'subtitle': f'Ученик • {highlight(s.phone, q)}',
            'url': f'/students/{s.id}/',
            'icon': 'bi-person',
            'is_active': s.is_active
        })
        
    for g in groups:
        results.append({
            'title': highlight(g.name, q),
            'subtitle': f'Группа • {g.get_course_type_display()}',
            'url': f'/groups/{g.id}/',
            'icon': 'bi-collection',
            'is_active': g.is_active
        })
        
    for t in teachers:
        results.append({
            'title': highlight(t.name, q),
            'subtitle': f'Учитель • {highlight(t.phone, q)}',
            'url': f'/teachers/{t.id}/',
            'icon': 'bi-person-workspace',
            'is_active': t.is_active
        })
        
    return render(request, 'components/search_results.html', {'results': results, 'q': q})
