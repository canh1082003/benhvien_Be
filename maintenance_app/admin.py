from django.contrib import admin
from .models import (AssetLocationHistory, AssetCustodyHistory, WorkOrder, Incident,
                     MaintenancePlan, CalibrationPlan, ChecklistTemplate, ChecklistTemplateItem,
                     WorkOrderChecklist, WorkOrderChecklistItem, ComplianceRecord, AssetEvent, AuditLog)


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('wo_code', 'asset', 'wo_type', 'priority', 'status', 'requested_at', 'due_at')
    list_filter = ('tenant', 'wo_type', 'status', 'priority')
    search_fields = ('wo_code', 'title', 'asset__asset_code')
    readonly_fields = ('requested_at', 'created_at', 'updated_at')


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_code', 'asset', 'symptom', 'priority', 'status', 'reported_at')
    list_filter = ('tenant', 'status', 'priority')
    search_fields = ('incident_code', 'symptom', 'asset__asset_code')


@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ('plan_code', 'name', 'asset', 'interval_type', 'interval_value', 'next_due_at', 'is_active')
    list_filter = ('tenant', 'is_active', 'interval_type')


@admin.register(CalibrationPlan)
class CalibrationPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_code', 'asset', 'type', 'interval_type', 'interval_value', 'next_due_at', 'is_active')
    list_filter = ('tenant', 'is_active', 'type')


@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ('record_code', 'asset', 'type', 'performed_at', 'next_due_at', 'result')
    list_filter = ('tenant', 'type', 'result')
    search_fields = ('record_code', 'asset__asset_code')


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'applies_to', 'version', 'is_active')
    list_filter = ('tenant', 'applies_to', 'is_active')


@admin.register(AssetEvent)
class AssetEventAdmin(admin.ModelAdmin):
    list_display = ('asset', 'event_type', 'event_time', 'summary', 'actor_user')
    list_filter = ('tenant', 'event_type')
    search_fields = ('asset__asset_code', 'summary')
    readonly_fields = ('event_time',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'entity_id', 'action', 'field_name', 'actor_user', 'acted_at')
    list_filter = ('tenant', 'entity_type', 'action')
    readonly_fields = ('acted_at',)


admin.site.register(AssetLocationHistory)
admin.site.register(AssetCustodyHistory)
admin.site.register(ChecklistTemplateItem)
admin.site.register(WorkOrderChecklist)
admin.site.register(WorkOrderChecklistItem)
