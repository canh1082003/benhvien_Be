from django.db import models
from core.models import Tenant, User
from locations_app.models import Department, Location


class Manufacturer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='manufacturers')
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'manufacturers'
        verbose_name = 'Nhà sản xuất'
        verbose_name_plural = 'Nhà sản xuất'

    def __str__(self):
        return self.name


class Vendor(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='vendors')
    name = models.CharField(max_length=200)
    tax_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    service_hotline = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'vendors'
        verbose_name = 'Nhà cung cấp'
        verbose_name_plural = 'Nhà cung cấp'

    def __str__(self):
        return self.name


class AssetCategory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='asset_categories')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'asset_categories'
        unique_together = ('tenant', 'code')
        verbose_name = 'Nhóm thiết bị'
        verbose_name_plural = 'Nhóm thiết bị'

    def __str__(self):
        return self.name


class AssetModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='asset_models')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='models')
    model_name = models.CharField(max_length=200)
    model_code = models.CharField(max_length=100, blank=True)
    spec_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'asset_models'
        verbose_name = 'Model thiết bị'
        verbose_name_plural = 'Model thiết bị'

    def __str__(self):
        return f"{self.manufacturer.name} {self.model_name}"


class Asset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('MAIN', 'Thiết bị chính'),
        ('ACCESSORY', 'Phụ kiện'),
        ('TOOL', 'Dụng cụ'),
    ]
    RISK_CLASS_CHOICES = [
        ('', 'Không phân loại'),
        ('Class A', 'Class A'),
        ('Class B', 'Class B'),
        ('Class C', 'Class C'),
        ('Class D', 'Class D'),
        ('Class I', 'Class I'),
        ('Class IIa', 'Class IIa'),
        ('Class IIb', 'Class IIb'),
        ('Class III', 'Class III'),
    ]
    CRITICALITY_CHOICES = [
        ('LOW', 'Thấp'),
        ('MEDIUM', 'Trung bình'),
        ('HIGH', 'Cao'),
        ('CRITICAL', 'Nghiêm trọng'),
    ]
    STATUS_CHOICES = [
        ('IN_SERVICE', 'Đang sử dụng'),
        ('STANDBY', 'Dự phòng'),
        ('UNDER_MAINTENANCE', 'Đang bảo trì'),
        ('BREAKDOWN', 'Hỏng'),
        ('OUT_OF_SERVICE', 'Ngừng hoạt động'),
        ('DECOMMISSIONED', 'Đã thanh lý'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='assets')
    asset_code = models.CharField(max_length=100, verbose_name='Mã thiết bị')
    asset_name = models.CharField(max_length=300, verbose_name='Tên thiết bị')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, default='MAIN', verbose_name='Loại')
    category = models.ForeignKey(AssetCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='assets', verbose_name='Nhóm/Chủng loại')
    model = models.ForeignKey(AssetModel, null=True, blank=True, on_delete=models.SET_NULL, related_name='assets', verbose_name='Model')
    manufacturer = models.ForeignKey(Manufacturer, null=True, blank=True, on_delete=models.SET_NULL, related_name='assets', verbose_name='Nhà sản xuất')
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name='assets', verbose_name='Nhà cung cấp')

    serial_no = models.CharField(max_length=100, blank=True, verbose_name='Serial Number')
    imei = models.CharField(max_length=50, blank=True, verbose_name='IMEI')
    barcode = models.CharField(max_length=100, blank=True, verbose_name='Barcode/QR')
    model_name_manual = models.CharField(max_length=200, blank=True, verbose_name='Model (nhập tay)')
    year_of_manufacture = models.IntegerField(null=True, blank=True, verbose_name='Năm sản xuất')

    risk_class = models.CharField(max_length=20, choices=RISK_CLASS_CHOICES, blank=True, verbose_name='Risk Class')
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES, default='MEDIUM', verbose_name='Mức độ ưu tiên')
    is_portable = models.BooleanField(default=False, verbose_name='Thiết bị di động')

    owner_dept = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_assets', verbose_name='Khoa/Phòng sở hữu')
    custodian_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='custodian_assets', verbose_name='Người phụ trách')
    current_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='assets', verbose_name='Vị trí hiện tại')
    current_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='IN_SERVICE', verbose_name='Trạng thái')

    commissioned_at = models.DateField(null=True, blank=True, verbose_name='Ngày đưa vào sử dụng')
    installed_at = models.DateField(null=True, blank=True, verbose_name='Ngày lắp đặt')
    purchase_at = models.DateField(null=True, blank=True, verbose_name='Ngày mua')
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Giá mua')
    warranty_start_at = models.DateField(null=True, blank=True, verbose_name='Bảo hành từ')
    warranty_end_at = models.DateField(null=True, blank=True, verbose_name='Bảo hành đến')
    expected_eol_at = models.DateField(null=True, blank=True, verbose_name='Ngày hết vòng đời (EOL)')
    useful_life_years = models.IntegerField(default=2, verbose_name='Vòng đời (năm)')

    # Inspection / PM tracking (from HTML design)
    inspection_required = models.BooleanField(default=True, verbose_name='Yêu cầu kiểm định')
    inspection_last_date = models.DateField(null=True, blank=True, verbose_name='Ngày kiểm định cuối')
    inspection_expiry_date = models.DateField(null=True, blank=True, verbose_name='Ngày hết hạn kiểm định')
    pm_required = models.BooleanField(default=True, verbose_name='Yêu cầu PM')
    pm_last_date = models.DateField(null=True, blank=True, verbose_name='Ngày PM cuối')
    pm_next_due_date = models.DateField(null=True, blank=True, verbose_name='Ngày PM kế tiếp')
    pm_interval_months = models.IntegerField(default=12, verbose_name='Chu kỳ PM (tháng)')

    # Contract
    service_contract_id = models.CharField(max_length=100, blank=True, verbose_name='Mã hợp đồng dịch vụ')
    contract_end = models.DateField(null=True, blank=True, verbose_name='Hết hạn hợp đồng')

    # Location detail (denormalized for easy display)
    building = models.CharField(max_length=100, blank=True, verbose_name='Tòa nhà')
    floor = models.CharField(max_length=50, blank=True, verbose_name='Tầng')
    room = models.CharField(max_length=100, blank=True, verbose_name='Phòng')
    bed = models.CharField(max_length=50, blank=True, verbose_name='Giường')
    ops_note = models.TextField(blank=True, verbose_name='Ghi chú vận hành')

    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    is_disabled = models.BooleanField(default=False, verbose_name='Vô hiệu hóa')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_assets')
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_assets')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'assets'
        unique_together = ('tenant', 'asset_code')
        indexes = [
            models.Index(fields=['tenant', 'asset_code']),
            models.Index(fields=['tenant', 'serial_no']),
            models.Index(fields=['tenant', 'current_status']),
            models.Index(fields=['tenant', 'owner_dept']),
        ]
        verbose_name = 'Thiết bị y tế'
        verbose_name_plural = 'Thiết bị y tế'

    def __str__(self):
        return f"{self.asset_code} – {self.asset_name}"

    def get_status_display_vi(self):
        return dict(self.STATUS_CHOICES).get(self.current_status, self.current_status)

    def get_status_badge_class(self):
        mapping = {
            'IN_SERVICE': 'b-green',
            'STANDBY': 'b-blue',
            'UNDER_MAINTENANCE': 'b-amber',
            'BREAKDOWN': 'b-red',
            'OUT_OF_SERVICE': 'b-gray',
            'DECOMMISSIONED': 'b-gray',
        }
        return mapping.get(self.current_status, 'b-gray')

    def inspection_status(self):
        from datetime import date
        if not self.inspection_required:
            return ('none', 'Không yêu cầu', '')
        if not self.inspection_expiry_date:
            return ('bad', 'Thiếu ngày hết hạn', 'b-red')
        today = date.today()
        delta = (self.inspection_expiry_date - today).days
        if delta < 0:
            return ('overdue', f'Quá hạn ({abs(delta)} ngày)', 'b-red')
        elif delta <= 30:
            return ('soon', f'Sắp đến hạn (còn {delta} ngày)', 'b-amber')
        else:
            return ('ok', f'Còn hạn (còn {delta} ngày)', 'b-green')

    def pm_status(self):
        from datetime import date
        if not self.pm_required:
            return ('none', 'Không yêu cầu', '')
        if not self.pm_next_due_date:
            return ('bad', 'Thiếu ngày PM', 'b-red')
        today = date.today()
        delta = (self.pm_next_due_date - today).days
        if delta < 0:
            return ('overdue', f'Quá hạn ({abs(delta)} ngày)', 'b-red')
        elif delta <= 30:
            return ('soon', f'Sắp đến hạn (còn {delta} ngày)', 'b-amber')
        else:
            return ('ok', f'Còn hạn (còn {delta} ngày)', 'b-green')

    def eol_status(self):
        from datetime import date
        if not self.commissioned_at or not self.useful_life_years:
            return ('bad', 'Thiếu thông tin EOL', 'b-red')
        try:
            eol = self.commissioned_at.replace(year=self.commissioned_at.year + self.useful_life_years)
        except ValueError:
            # Feb 29 edge case for non-leap target year
            import datetime
            eol = self.commissioned_at + datetime.timedelta(days=365 * self.useful_life_years)
        today = date.today()
        delta = (eol - today).days
        if delta < 0:
            return ('expired', f'Hết hạn ({abs(delta)} ngày)', 'b-red')
        elif delta <= 60:
            return ('soon', f'Sắp hết (còn {delta} ngày)', 'b-amber')
        else:
            return ('ok', f'Trong vòng đời (còn {delta} ngày)', 'b-green')


class AssetStatusHistory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    reason_code = models.CharField(max_length=50, blank=True)
    reason_note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'asset_status_history'
        indexes = [models.Index(fields=['tenant', 'asset', '-changed_at'])]
        verbose_name = 'Lịch sử trạng thái'
        verbose_name_plural = 'Lịch sử trạng thái'


class AssetHierarchy(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    parent_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='child_links')
    child_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='parent_links')
    relation_type = models.CharField(max_length=50, default='COMPONENT')

    class Meta:
        db_table = 'asset_hierarchy'
        unique_together = ('parent_asset', 'child_asset')
        verbose_name = 'Phân cấp thiết bị'
        verbose_name_plural = 'Phân cấp thiết bị'
