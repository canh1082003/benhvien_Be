from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Tenant, User, Role, Permission, UserRole, RolePermission


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'timezone', 'created_at')
    search_fields = ('code', 'name')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'email', 'tenant', 'is_active', 'is_staff')
    list_filter = ('tenant', 'is_active', 'is_staff')
    search_fields = ('username', 'full_name', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin thêm', {'fields': ('tenant', 'full_name', 'phone', 'dept_id')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'code', 'name')
    list_filter = ('tenant',)


admin.site.register(Permission)
admin.site.register(UserRole)
admin.site.register(RolePermission)
