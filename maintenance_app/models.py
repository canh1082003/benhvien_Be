from django.db import models
from core.models import Tenant, User
from assets_app.models import Asset
from locations_app.models import Department, Location


class AssetLocationHistory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='location_history')
    from_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='+')
    moved_at = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    reason_code = models.CharField(max_length=50, blank=True)
    reason_note = models.TextField(blank=True)

    class Meta:
        db_table = 'asset_location_history'
        indexes = [models.Index(fields=['tenant', 'asset', '-moved_at'])]
        verbose_name = 'Lịch sử di chuyển'
        verbose_name_plural = 'Lịch sử di chuyển'


class AssetCustodyHistory(models.Model):
    HANDOVER_TYPE_CHOICES = [
        ('PERMANENT', 'Bàn giao vĩnh viễn'),
        ('LOAN', 'Cho mượn'),
        ('SEND_REPAIR', 'Gửi sửa chữa'),
        ('RETURN', 'Hoàn trả'),
        ('OTHER', 'Khác'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Nháp'),
        ('PENDING', 'Chờ xác nhận'),
        ('COMPLETED', 'Hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='custody_history')
    handover_type = models.CharField(max_length=20, choices=HANDOVER_TYPE_CHOICES)
    from_dept = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    to_dept = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    from_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='handovers_from')
    to_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='handovers_to')
    from_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    to_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    handover_at = models.DateTimeField(auto_now_add=True)
    expected_return_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    accessories_verified = models.BooleanField(default=False)
    accessories_verification_note = models.TextField(blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'asset_custody_history'
        indexes = [models.Index(fields=['tenant', 'asset', '-handover_at'])]
        verbose_name = 'Lịch sử bàn giao'
        verbose_name_plural = 'Lịch sử bàn giao'

    def __str__(self):
        return f"Bàn giao {self.asset.asset_code} – {self.handover_at.date()}"


class WorkOrder(models.Model):
    WO_TYPE_CHOICES = [
        ('PM', 'Bảo trì định kỳ'),
        ('REPAIR', 'Sửa chữa'),
        ('CALIBRATION', 'Hiệu chuẩn'),
        ('INSPECTION', 'Kiểm định'),
    ]
    PRIORITY_CHOICES = [
        ('LOW', 'Thấp'),
        ('MEDIUM', 'Trung bình'),
        ('HIGH', 'Cao'),
        ('CRITICAL', 'Nghiêm trọng'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Nháp'),
        ('OPEN', 'Mở'),
        ('ASSIGNED', 'Đã phân công'),
        ('IN_PROGRESS', 'Đang thực hiện'),
        ('WAIT_PARTS', 'Chờ linh kiện'),
        ('WAIT_VENDOR', 'Chờ vendor'),
        ('COMPLETED', 'Hoàn thành'),
        ('CLOSED', 'Đóng'),
        ('CANCELLED', 'Đã hủy'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    wo_code = models.CharField(max_length=50, unique=True, verbose_name='Mã Work Order')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='work_orders')
    wo_type = models.CharField(max_length=20, choices=WO_TYPE_CHOICES, verbose_name='Loại')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    title = models.CharField(max_length=300, verbose_name='Tiêu đề')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    requested_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='created_work_orders')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_work_orders')
    vendor = models.ForeignKey('assets_app.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    downtime_start_at = models.DateTimeField(null=True, blank=True)
    downtime_end_at = models.DateTimeField(null=True, blank=True)
    cost_labor = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    cost_parts = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    cost_vendor = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    cost_total = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'work_orders'
        indexes = [
            models.Index(fields=['tenant', 'asset', '-requested_at']),
            models.Index(fields=['tenant', 'wo_type', 'status']),
        ]
        verbose_name = 'Work Order'
        verbose_name_plural = 'Work Orders'

    def __str__(self):
        return f"{self.wo_code} – {self.title}"


class Incident(models.Model):
    STATUS_CHOICES = [
        ('REPORTED', 'Đã báo cáo'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('IN_PROGRESS', 'Đang xử lý'),
        ('RESOLVED', 'Đã giải quyết'),
        ('CLOSED', 'Đóng'),
        ('CANCELLED', 'Đã hủy'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    incident_code = models.CharField(max_length=50, unique=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='incidents')
    reported_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='reported_incidents')
    symptom = models.CharField(max_length=300, verbose_name='Triệu chứng')
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=WorkOrder.PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REPORTED')
    work_order = models.ForeignKey(WorkOrder, null=True, blank=True, on_delete=models.SET_NULL, related_name='incidents')
    root_cause_code = models.CharField(max_length=50, blank=True)
    root_cause_note = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'incidents'
        indexes = [models.Index(fields=['tenant', 'asset', '-reported_at'])]
        verbose_name = 'Sự cố/Báo hỏng'
        verbose_name_plural = 'Sự cố/Báo hỏng'

    def __str__(self):
        return f"{self.incident_code} – {self.symptom}"


class MaintenancePlan(models.Model):
    INTERVAL_TYPE_CHOICES = [
        ('DAY', 'Ngày'),
        ('MONTH', 'Tháng'),
        ('YEAR', 'Năm'),
        ('USAGE_HOURS', 'Giờ sử dụng'),
        ('CYCLES', 'Chu kỳ'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_plans')
    plan_code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    interval_type = models.CharField(max_length=20, choices=INTERVAL_TYPE_CHOICES)
    interval_value = models.IntegerField()
    next_due_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maintenance_plans'
        verbose_name = 'Kế hoạch PM'
        verbose_name_plural = 'Kế hoạch PM'

    def __str__(self):
        return f"{self.plan_code} – {self.name}"


class CalibrationPlan(models.Model):
    TYPE_CHOICES = [
        ('CALIBRATION', 'Hiệu chuẩn'),
        ('VERIFICATION', 'Kiểm tra'),
        ('SAFETY_TEST', 'Kiểm tra an toàn'),
        ('INSPECTION', 'Kiểm định'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='calibration_plans')
    plan_code = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    interval_type = models.CharField(max_length=20, choices=MaintenancePlan.INTERVAL_TYPE_CHOICES)
    interval_value = models.IntegerField()
    next_due_at = models.DateField(null=True, blank=True)
    vendor = models.ForeignKey('assets_app.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calibration_plans'
        verbose_name = 'Kế hoạch kiểm định'
        verbose_name_plural = 'Kế hoạch kiểm định'


class ChecklistTemplate(models.Model):
    APPLIES_TO_CHOICES = [
        ('PM', 'Bảo trì'),
        ('REPAIR', 'Sửa chữa'),
        ('CALIBRATION', 'Hiệu chuẩn'),
        ('INSPECTION', 'Kiểm định'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO_CHOICES)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'checklist_templates'
        verbose_name = 'Mẫu checklist'
        verbose_name_plural = 'Mẫu checklist'

    def __str__(self):
        return f"{self.code} – {self.name}"


class ChecklistTemplateItem(models.Model):
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, related_name='items')
    seq_no = models.IntegerField()
    item_name = models.CharField(max_length=300)
    expected_result = models.TextField(blank=True)
    is_critical = models.BooleanField(default=False)
    evidence_required = models.BooleanField(default=False)
    measurement_unit = models.CharField(max_length=50, blank=True)
    min_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    class Meta:
        db_table = 'checklist_template_items'
        ordering = ['seq_no']


class WorkOrderChecklist(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Chưa bắt đầu'),
        ('IN_PROGRESS', 'Đang thực hiện'),
        ('COMPLETED', 'Hoàn thành'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='checklists')
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'work_order_checklists'


class WorkOrderChecklistItem(models.Model):
    RESULT_CHOICES = [
        ('PASS', 'Đạt'),
        ('FAIL', 'Không đạt'),
        ('NA', 'Không áp dụng'),
    ]

    wo_checklist = models.ForeignKey(WorkOrderChecklist, on_delete=models.CASCADE, related_name='items')
    template_item = models.ForeignKey(ChecklistTemplateItem, on_delete=models.CASCADE)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, null=True, blank=True)
    measured_value = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'work_order_checklist_items'


class ComplianceRecord(models.Model):
    TYPE_CHOICES = [
        ('CALIBRATION', 'Hiệu chuẩn'),
        ('VERIFICATION', 'Kiểm tra'),
        ('SAFETY_TEST', 'Kiểm tra an toàn'),
        ('INSPECTION', 'Kiểm định'),
    ]
    PERFORMED_BY_TYPE_CHOICES = [
        ('INTERNAL', 'Nội bộ'),
        ('VENDOR', 'Vendor'),
        ('LAB', 'Phòng lab'),
    ]
    RESULT_CHOICES = [
        ('PASS', 'Đạt'),
        ('FAIL', 'Không đạt'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    record_code = models.CharField(max_length=50, unique=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='compliance_records')
    source_wo = models.ForeignKey(WorkOrder, null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    performed_by_type = models.CharField(max_length=20, choices=PERFORMED_BY_TYPE_CHOICES, default='VENDOR')
    vendor = models.ForeignKey('assets_app.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    performed_at = models.DateField()
    next_due_at = models.DateField(null=True, blank=True)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    note = models.TextField(blank=True)
    certificate_file = models.FileField(upload_to='compliance/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compliance_records'
        indexes = [models.Index(fields=['tenant', 'asset', '-performed_at'])]
        verbose_name = 'Hồ sơ kiểm định/hiệu chuẩn'
        verbose_name_plural = 'Hồ sơ kiểm định/hiệu chuẩn'

    def __str__(self):
        return f"{self.record_code} – {self.get_type_display()}"


class AssetEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('STATUS', 'Thay đổi trạng thái'),
        ('MOVE', 'Di chuyển'),
        ('HANDOVER', 'Bàn giao'),
        ('WO', 'Work Order'),
        ('INCIDENT', 'Sự cố'),
        ('COMPLIANCE', 'Kiểm định/Hiệu chuẩn'),
        ('PART', 'Linh kiện'),
        ('DOC', 'Tài liệu'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_time = models.DateTimeField()
    ref_type = models.CharField(max_length=50, blank=True)
    ref_id = models.BigIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=500)
    actor_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    payload_json = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'asset_events'
        indexes = [models.Index(fields=['tenant', 'asset', '-event_time'])]
        verbose_name = 'Sự kiện thiết bị'
        verbose_name_plural = 'Sự kiện thiết bị'


class AuditLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    entity_type = models.CharField(max_length=50)
    entity_id = models.BigIntegerField()
    action = models.CharField(max_length=50)
    field_name = models.CharField(max_length=100, blank=True)
    before_value = models.TextField(blank=True)
    after_value = models.TextField(blank=True)
    actor_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    acted_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        indexes = [models.Index(fields=['tenant', 'entity_type', 'entity_id', '-acted_at'])]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
