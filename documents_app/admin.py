from django.contrib import admin
from .models import DocumentGroup, Document


@admin.register(DocumentGroup)
class DocumentGroupAdmin(admin.ModelAdmin):
    list_display = ('group_type', 'ref_id', 'tenant', 'created_at')
    list_filter = ('tenant', 'group_type')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'doc_type', 'group', 'uploaded_at', 'uploaded_by')
    list_filter = ('tenant', 'doc_type')
    search_fields = ('file_name',)
