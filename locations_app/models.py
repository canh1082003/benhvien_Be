from django.db import models
from core.models import Tenant, User


class Department(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='departments')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'departments'
        unique_together = ('tenant', 'code')
        verbose_name = 'Khoa/Phòng'
        verbose_name_plural = 'Khoa/Phòng'

    def __str__(self):
        return self.name


class Location(models.Model):
    TYPE_CHOICES = [
        ('BRANCH', 'Chi nhánh'),
        ('BUILDING', 'Tòa nhà'),
        ('FLOOR', 'Tầng'),
        ('DEPARTMENT_AREA', 'Khu vực khoa'),
        ('ROOM', 'Phòng'),
        ('BED', 'Giường'),
        ('WAREHOUSE', 'Kho'),
        ('OTHER', 'Khác'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='locations')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    dept = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='locations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'locations'
        indexes = [
            models.Index(fields=['tenant', 'parent']),
            models.Index(fields=['tenant', 'type']),
        ]
        verbose_name = 'Vị trí'
        verbose_name_plural = 'Vị trí'

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def full_path(self):
        parts = [self.name]
        parent = self.parent
        while parent:
            parts.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(parts)
