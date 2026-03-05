from django.contrib import admin
from .models import (Manufacturer, Vendor, AssetCategory, AssetModel,
                     Asset, AssetStatusHistory, AssetHierarchy)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('name', 'country')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_code', 'phone', 'email', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('name', 'tax_code')


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('code', 'name')


@admin.register(AssetModel)
class AssetModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_code', 'manufacturer', 'tenant')
    list_filter = ('tenant', 'manufacturer')
    search_fields = ('model_name', 'model_code')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_code', 'asset_name', 'category', 'owner_dept',
                    'current_status', 'commissioned_at', 'pm_next_due_date', 'tenant')
    list_filter = ('tenant', 'current_status', 'asset_type', 'category', 'owner_dept')
    search_fields = ('asset_code', 'asset_name', 'serial_no', 'imei', 'barcode')
    date_hierarchy = 'commissioned_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Nhận diện', {
            'fields': ('tenant', 'asset_code', 'asset_name', 'asset_type',
                       'serial_no', 'imei', 'barcode')
        }),
        ('Phân loại', {
            'fields': ('category', 'model', 'manufacturer', 'model_name_manual',
                       'year_of_manufacture', 'risk_class', 'criticality', 'is_portable')
        }),
        ('Phân bổ & Vị trí', {
            'fields': ('owner_dept', 'custodian_user', 'current_location',
                       'current_status', 'building', 'floor', 'room', 'bed', 'ops_note')
        }),
        ('Kiểm định/PM/Vòng đời', {
            'fields': ('inspection_required', 'inspection_last_date', 'inspection_expiry_date',
                       'pm_required', 'pm_last_date', 'pm_next_due_date',
                       'commissioned_at', 'useful_life_years', 'expected_eol_at')
        }),
        ('Hợp đồng', {
            'fields': ('vendor', 'warranty_start_at', 'warranty_end_at',
                       'service_contract_id', 'contract_end', 'purchase_at')
        }),
        ('Ghi chú', {'fields': ('notes', 'is_disabled')}),
        ('Hệ thống', {'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'), 'classes': ('collapse',)}),
    )


@admin.register(AssetStatusHistory)
class AssetStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('asset', 'from_status', 'to_status', 'changed_at', 'changed_by')
    list_filter = ('tenant', 'to_status')
    readonly_fields = ('changed_at',)


admin.site.register(AssetHierarchy)
