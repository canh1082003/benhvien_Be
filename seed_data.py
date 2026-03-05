import os
import sys
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benhvien_django.settings')
django.setup()

from core.models import Tenant
from locations_app.models import Department, Location
from assets_app.models import Manufacturer, Vendor, AssetCategory, Asset

print("🌱 Bắt đầu seed dữ liệu mẫu...")

# ── 1. Tenant ──────────────────────────────────────────────────────────────
tenant, _ = Tenant.objects.get_or_create(
    code='DEFAULT',
    defaults={'name': 'Bệnh Viện Đa Khoa Trung Tâm', 'timezone': 'Asia/Ho_Chi_Minh'}
)
print(f"  ✅ Tenant: {tenant.name}")

# ── 2. Khoa/Phòng ─────────────────────────────────────────────────────────
depts_data = [
    ('ICU', 'Khoa Hồi sức Tích cực (ICU)'),
    ('PHONG-MY', 'Phòng Mổ'),
    ('NOI-TCH', 'Khoa Nội Tổng hợp'),
    ('CHAN-DOAN', 'Khoa Chẩn đoán Hình ảnh'),
    ('XET-NGHIEM', 'Khoa Xét nghiệm'),
    ('CAP-CUU', 'Khoa Cấp cứu'),
    ('NHI', 'Khoa Nhi'),
    ('KHO-VT', 'Kho Vật tư Y tế'),
]
depts = {}
for code, name in depts_data:
    d, _ = Department.objects.get_or_create(tenant=tenant, code=code, defaults={'name': name})
    depts[code] = d
print(f"  ✅ {len(depts)} Khoa/Phòng")

# ── 3. Nhóm thiết bị ──────────────────────────────────────────────────────
cats_data = [
    ('THEODOI', 'Thiết bị theo dõi'),
    ('HO-HAP', 'Thiết bị hỗ trợ hô hấp'),
    ('HINH-ANH', 'Thiết bị chẩn đoán hình ảnh'),
    ('XET-NGHIEM', 'Thiết bị xét nghiệm'),
    ('PHAU-THUAT', 'Thiết bị phẫu thuật'),
    ('VAT-LY-TRI-LIEU', 'Thiết bị vật lý trị liệu'),
]
cats = {}
for code, name in cats_data:
    c, _ = AssetCategory.objects.get_or_create(tenant=tenant, code=code, defaults={'name': name})
    cats[code] = c
print(f"  ✅ {len(cats)} Nhóm thiết bị")

# ── 4. Nhà sản xuất ───────────────────────────────────────────────────────
mfrs_data = [
    ('Philips Healthcare', 'Netherlands'),
    ('GE Healthcare', 'USA'),
    ('Siemens Healthineers', 'Germany'),
    ('Mindray', 'China'),
    ('Drager', 'Germany'),
]
mfrs = {}
for name, country in mfrs_data:
    m, _ = Manufacturer.objects.get_or_create(tenant=tenant, name=name, defaults={'country': country})
    mfrs[name] = m
print(f"  ✅ {len(mfrs)} Nhà sản xuất")

# ── 5. Nhà cung cấp ───────────────────────────────────────────────────────
vendor, _ = Vendor.objects.get_or_create(
    tenant=tenant, name='Công ty CP Thiết bị Y tế Tân Phát',
    defaults={'phone': '028-3812-3456', 'email': 'info@tanphat.vn'}
)

# ── 6. Thiết bị Y tế mẫu ─────────────────────────────────────────────────
today = date.today()

assets_data = [
    # (code, name, category_code, dept_code, status, manufacturer, room, insp_expiry_delta, pm_next_delta, risk)
    ('TB-ICU-001', 'Máy theo dõi bệnh nhân đa thông số IntelliVue MX450',
     'THEODOI', 'ICU', 'IN_SERVICE', 'Philips Healthcare', 'Phòng ICU 01',
     90, 45, 'Class IIb'),
    ('TB-ICU-002', 'Máy thở ICU Evita Infinity V500',
     'HO-HAP', 'ICU', 'IN_SERVICE', 'Drager', 'Phòng ICU 02',
     -5, -10, 'Class III'),   # quá hạn kiểm định
    ('TB-ICU-003', 'Bơm tiêm điện Injekt-F',
     'THEODOI', 'ICU', 'IN_SERVICE', 'Drager', 'Phòng ICU 03',
     25, 20, 'Class IIa'),    # sắp đến hạn
    ('TB-MY-001', 'Dao điện phẫu thuật FORCE FX',
     'PHAU-THUAT', 'PHONG-MY', 'IN_SERVICE', 'GE Healthcare', 'Phòng Mổ 1',
     200, 180, 'Class IIb'),
    ('TB-MY-002', 'Máy gây mê Flow-C',
     'HO-HAP', 'PHONG-MY', 'UNDER_MAINTENANCE', 'Drager', 'Phòng Mổ 2',
     150, -3, 'Class III'),   # đang bảo trì, PM quá hạn
    ('TB-CDA-001', 'Máy siêu âm tổng quát LOGIQ E10',
     'HINH-ANH', 'CHAN-DOAN', 'IN_SERVICE', 'GE Healthcare', 'Phòng SA 01',
     365, 120, 'Class IIa'),
    ('TB-CDA-002', 'Máy X-quang kỹ thuật số DR 600',
     'HINH-ANH', 'CHAN-DOAN', 'IN_SERVICE', 'Siemens Healthineers', 'Phòng XQ 01',
     -30, 60, 'Class IIb'),   # quá hạn kiểm định
    ('TB-XN-001', 'Máy phân tích huyết học tự động XN-L Series',
     'XET-NGHIEM', 'XET-NGHIEM', 'IN_SERVICE', 'Mindray', 'Phòng XN Huyết học',
     180, 90, 'Class IIa'),
    ('TB-XN-002', 'Máy sinh hóa tự động BS-2000M',
     'XET-NGHIEM', 'XET-NGHIEM', 'STANDBY', 'Mindray', 'Phòng XN Sinh hóa',
     270, 150, 'Class IIa'),
    ('TB-NOI-001', 'Máy đo ECG 12 kênh ELI 280',
     'THEODOI', 'NOI-TCH', 'IN_SERVICE', 'Mindray', 'Phòng Đo điện tim',
     15, 10, 'Class IIa'),    # sắp đến hạn cả 2
    ('TB-CC-001', 'Máy khử rung tim (AED) HeartStart MRx',
     'THEODOI', 'CAP-CUU', 'IN_SERVICE', 'Philips Healthcare', 'Phòng Cấp cứu',
     400, 365, 'Class III'),
    ('TB-NHI-001', 'Lồng ấp trẻ sơ sinh Caleo',
     'THEODOI', 'NHI', 'BREAKDOWN', 'Drager', 'Phòng Sơ sinh',
     -60, 300, 'Class IIb'),  # hỏng, quá hạn kiểm định
]

created = 0
for item in assets_data:
    code, name, cat_code, dept_code, status, mfr_name, room, insp_delta, pm_delta, risk = item

    insp_expiry = today + timedelta(days=insp_delta)
    insp_last = insp_expiry - timedelta(days=365)
    pm_next = today + timedelta(days=pm_delta)
    pm_last = pm_next - timedelta(days=90)
    commissioned = today - timedelta(days=730)  # 2 năm trước
    warranty_end = today + timedelta(days=365)

    asset, created_flag = Asset.objects.get_or_create(
        tenant=tenant,
        asset_code=code,
        defaults=dict(
            asset_name=name,
            category=cats.get(cat_code),
            owner_dept=depts.get(dept_code),
            current_status=status,
            manufacturer=mfrs.get(mfr_name),
            vendor=vendor,
            risk_class=risk,
            criticality='HIGH',
            room=room,
            building='Tòa A',
            floor='Tầng 2',
            inspection_required=True,
            inspection_last_date=insp_last,
            inspection_expiry_date=insp_expiry,
            pm_required=True,
            pm_last_date=pm_last,
            pm_next_due_date=pm_next,
            commissioned_at=commissioned,
            useful_life_years=7,
            warranty_start_at=commissioned,
            warranty_end_at=warranty_end,
            serial_no=f'SN{code.replace("-", "")[:10]}2024',
        )
    )
    if created_flag:
        created += 1
        print(f"    + {code}: {name[:50]}... [{status}]")

print(f"\n✅ Đã tạo {created}/{len(assets_data)} thiết bị mẫu.")
print("\n🎉 Seed dữ liệu hoàn tất! Mở http://127.0.0.1:8080/ để xem.")
