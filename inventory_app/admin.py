from django.contrib import admin
from .models import Part, Inventory, InventoryLot, PartIssue, PartIssueItem, AssetAccessory


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('part_code', 'part_name', 'uom', 'is_lot_tracked', 'tenant')
    list_filter = ('tenant', 'is_lot_tracked', 'is_expiry_tracked')
    search_fields = ('part_code', 'part_name')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('part', 'store_location', 'on_hand_qty', 'min_qty', 'tenant')
    list_filter = ('tenant',)


@admin.register(PartIssue)
class PartIssueAdmin(admin.ModelAdmin):
    list_display = ('issue_code', 'asset', 'work_order', 'issued_at', 'issued_by')
    list_filter = ('tenant',)
    search_fields = ('issue_code',)


@admin.register(AssetAccessory)
class AssetAccessoryAdmin(admin.ModelAdmin):
    list_display = ('accessory_name', 'asset', 'quantity', 'status', 'is_mandatory')
    list_filter = ('tenant', 'status', 'is_mandatory')
    search_fields = ('accessory_name', 'asset__asset_code')


admin.site.register(InventoryLot)
admin.site.register(PartIssueItem)
