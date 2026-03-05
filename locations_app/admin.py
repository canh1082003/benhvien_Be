from django.contrib import admin
from .models import Department, Location


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('code', 'name')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'parent', 'dept', 'tenant')
    list_filter = ('tenant', 'type')
    search_fields = ('code', 'name')
