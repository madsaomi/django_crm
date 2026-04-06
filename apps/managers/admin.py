from django.contrib import admin
from .models import Manager


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'created_at']
    search_fields = ['name', 'phone']
