from django.db import models
from core.models import Tenant, User
from assets_app.models import Asset
from locations_app.models import Location


class Part(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='parts')
    part_code = models.CharField(max_length=100)
    part_name = models.CharField(max_length=300, verbose_name='Tên linh kiện')
    uom = models.CharField(max_length=20, blank=True, verbose_name='Đơn vị tính')
    is_lot_tracked = models.BooleanField(default=False)
    is_expiry_tracked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'parts'
        unique_together = ('tenant', 'part_code')
        verbose_name = 'Linh kiện/Vật tư'
        verbose_name_plural = 'Linh kiện/Vật tư'

    def __str__(self):
        return f"{self.part_code} – {self.part_name}"


class Inventory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    store_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='inventories')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='inventories')
    on_hand_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    min_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reorder_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventories'
        unique_together = ('tenant', 'store_location', 'part')
        verbose_name = 'Tồn kho'
        verbose_name_plural = 'Tồn kho'


class InventoryLot(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    store_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='lots')
    lot_no = models.CharField(max_length=100)
    expiry_at = models.DateField(null=True, blank=True)
    qty_on_hand = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    class Meta:
        db_table = 'inventory_lots'
        unique_together = ('tenant', 'store_location', 'part', 'lot_no')
        verbose_name = 'Lô linh kiện'
        verbose_name_plural = 'Lô linh kiện'


class PartIssue(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    issue_code = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    store_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    work_order = models.ForeignKey('maintenance_app.WorkOrder', null=True, blank=True, on_delete=models.SET_NULL, related_name='part_issues')
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.SET_NULL, related_name='part_issues')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'part_issues'
        verbose_name = 'Phiếu xuất kho'
        verbose_name_plural = 'Phiếu xuất kho'

    def __str__(self):
        return self.issue_code


class PartIssueItem(models.Model):
    issue = models.ForeignKey(PartIssue, on_delete=models.CASCADE, related_name='items')
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    lot = models.ForeignKey(InventoryLot, null=True, blank=True, on_delete=models.SET_NULL)
    qty = models.DecimalField(max_digits=12, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)

    class Meta:
        db_table = 'part_issue_items'


class AssetAccessory(models.Model):
    STATUS_CHOICES = [
        ('OK', 'Bình thường'),
        ('MISSING', 'Thiếu'),
        ('DAMAGED', 'Hỏng'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='accessories')
    accessory_name = models.CharField(max_length=200, verbose_name='Tên phụ kiện')
    part = models.ForeignKey(Part, null=True, blank=True, on_delete=models.SET_NULL)
    serial_no = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OK')
    is_mandatory = models.BooleanField(default=False)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    last_verified_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_accessories'
        indexes = [models.Index(fields=['tenant', 'asset'])]
        verbose_name = 'Phụ kiện thiết bị'
        verbose_name_plural = 'Phụ kiện thiết bị'

    def __str__(self):
        return f"{self.accessory_name} – {self.asset.asset_code}"
