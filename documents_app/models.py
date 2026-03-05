from django.db import models
from core.models import Tenant, User


class DocumentGroup(models.Model):
    GROUP_TYPE_CHOICES = [
        ('ASSET', 'Thiết bị'),
        ('WO', 'Work Order'),
        ('INCIDENT', 'Sự cố'),
        ('HANDOVER', 'Bàn giao'),
        ('COMPLIANCE', 'Kiểm định/Hiệu chuẩn'),
        ('CHECKLIST_ITEM', 'Mục checklist'),
        ('OTHER', 'Khác'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    group_type = models.CharField(max_length=30, choices=GROUP_TYPE_CHOICES)
    ref_id = models.BigIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_groups'
        verbose_name = 'Nhóm tài liệu'
        verbose_name_plural = 'Nhóm tài liệu'


class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ('MANUAL', 'Hướng dẫn sử dụng'),
        ('SOP', 'Quy trình'),
        ('CERTIFICATE', 'Chứng chỉ'),
        ('REPORT', 'Báo cáo'),
        ('PHOTO', 'Ảnh'),
        ('VIDEO', 'Video'),
        ('HANDOVER_FORM', 'Biên bản bàn giao'),
        ('OTHER', 'Khác'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    group = models.ForeignKey(DocumentGroup, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    file_name = models.CharField(max_length=300)
    file = models.FileField(upload_to='documents/%Y/%m/')
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    version_no = models.IntegerField(default=1)

    class Meta:
        db_table = 'documents'
        indexes = [models.Index(fields=['tenant', 'group', '-uploaded_at'])]
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'

    def __str__(self):
        return self.file_name
