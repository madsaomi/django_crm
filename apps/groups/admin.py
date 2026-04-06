from django.contrib import admin
from .models import Group, Enrollment, SundayEvent


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_type', 'teacher', 'schedule_type', 'time_slot', 'room', 'monthly_fee', 'students_count', 'max_students']
    list_filter = ['course_type', 'schedule_type', 'is_active']
    search_fields = ['name']
    inlines = [EnrollmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'enrolled_date', 'is_active']
    list_filter = ['is_active', 'group']


@admin.register(SundayEvent)
class SundayEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time_slot', 'room', 'teacher']
    list_filter = ['date']
    search_fields = ['title', 'room']
