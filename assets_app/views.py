from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from datetime import date
from .models import Asset, AssetCategory, Manufacturer
from .forms import AssetForm
from core.models import Tenant
from locations_app.models import Department
from maintenance_app.models import WorkOrder, Incident, ComplianceRecord, AssetEvent


def get_default_tenant():
    """Lấy tenant mặc định (single-tenant mode)"""
    tenant, _ = Tenant.objects.get_or_create(
        code='DEFAULT',
        defaults={'name': 'Bệnh Viện', 'timezone': 'Asia/Ho_Chi_Minh'}
    )
    return tenant


def asset_list(request):
    tenant = get_default_tenant()
    assets = Asset.objects.filter(tenant=tenant, is_deleted=False).select_related(
        'category', 'owner_dept', 'manufacturer', 'custodian_user', 'vendor'
    )

    # Search & Filter
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    dept_filter = request.GET.get('dept', '')
    inspection_filter = request.GET.get('inspection', '')
    pm_filter = request.GET.get('pm', '')
    quick_filter = request.GET.get('qf', '')

    if q:
        assets = assets.filter(
            Q(asset_code__icontains=q) |
            Q(asset_name__icontains=q) |
            Q(serial_no__icontains=q) |
            Q(imei__icontains=q) |
            Q(barcode__icontains=q)
        )

    if status_filter:
        assets = assets.filter(current_status=status_filter)

    if dept_filter:
        assets = assets.filter(owner_dept_id=dept_filter)

    today = date.today()

    # Quick filters
    if quick_filter == 'inspection_due_soon':
        assets = assets.filter(
            inspection_required=True,
            inspection_expiry_date__gte=today,
            inspection_expiry_date__lte=date.fromordinal(today.toordinal() + 30)
        )
    elif quick_filter == 'inspection_overdue':
        assets = assets.filter(inspection_required=True, inspection_expiry_date__lt=today)
    elif quick_filter == 'pm_due_soon':
        assets = assets.filter(
            pm_required=True,
            pm_next_due_date__gte=today,
            pm_next_due_date__lte=date.fromordinal(today.toordinal() + 30)
        )
    elif quick_filter == 'pm_overdue':
        assets = assets.filter(pm_required=True, pm_next_due_date__lt=today)
    elif quick_filter == 'broken':
        assets = assets.filter(current_status='BREAKDOWN')

    assets_list = list(assets.order_by('-updated_at'))

    # KPI counts
    all_assets = Asset.objects.filter(tenant=tenant, is_deleted=False)
    kpi_total = all_assets.count()
    kpi_in_use = all_assets.filter(current_status='IN_SERVICE').count()
    kpi_standby = all_assets.filter(current_status='STANDBY').count()
    kpi_broken = all_assets.filter(current_status='BREAKDOWN').count()
    kpi_inspect_soon = all_assets.filter(
        inspection_required=True,
        inspection_expiry_date__gte=today,
        inspection_expiry_date__lte=date.fromordinal(today.toordinal() + 30)
    ).count()
    kpi_inspect_overdue = all_assets.filter(
        inspection_required=True, inspection_expiry_date__lt=today
    ).count()
    kpi_pm_soon = all_assets.filter(
        pm_required=True,
        pm_next_due_date__gte=today,
        pm_next_due_date__lte=date.fromordinal(today.toordinal() + 30)
    ).count()
    kpi_pm_overdue = all_assets.filter(pm_required=True, pm_next_due_date__lt=today).count()

    # Filters dropdowns
    departments = Department.objects.filter(tenant=tenant, is_deleted=False)

    context = {
        'assets': assets_list,
        'q': q,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'quick_filter': quick_filter,
        'departments': departments,
        'kpi_total': kpi_total,
        'kpi_in_use': kpi_in_use,
        'kpi_standby': kpi_standby,
        'kpi_broken': kpi_broken,
        'kpi_inspect_soon': kpi_inspect_soon,
        'kpi_inspect_overdue': kpi_inspect_overdue,
        'kpi_pm_soon': kpi_pm_soon,
        'kpi_pm_overdue': kpi_pm_overdue,
        'today': today,
    }
    return render(request, 'assets/list.html', context)


def asset_add(request):
    tenant = get_default_tenant()

    if request.method == 'POST':
        form = AssetForm(request.POST, tenant=tenant)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.tenant = tenant
            asset.save()
            messages.success(request, f'Đã thêm thiết bị {asset.asset_code} thành công!')

            # Create asset event
            AssetEvent.objects.create(
                tenant=tenant,
                asset=asset,
                event_type='STATUS',
                event_time=asset.created_at,
                summary=f'Thiết bị {asset.asset_code} được nhập mới vào hệ thống.'
            )
            return redirect('asset_detail', pk=asset.pk)
    else:
        form = AssetForm(tenant=tenant)

    categories = AssetCategory.objects.filter(tenant=tenant, is_deleted=False)
    departments = Department.objects.filter(tenant=tenant, is_deleted=False)

    context = {
        'form': form,
        'categories': categories,
        'departments': departments,
        'page_title': 'Nhập mới thiết bị y tế',
    }
    return render(request, 'assets/add.html', context)


def asset_detail(request, pk):
    tenant = get_default_tenant()
    asset = get_object_or_404(Asset, pk=pk, tenant=tenant, is_deleted=False)

    # Related data
    work_orders = WorkOrder.objects.filter(asset=asset, is_deleted=False).order_by('-requested_at')[:20]
    incidents = Incident.objects.filter(asset=asset, is_deleted=False).order_by('-reported_at')[:20]
    compliance_records = ComplianceRecord.objects.filter(asset=asset).order_by('-performed_at')[:20]
    events = AssetEvent.objects.filter(asset=asset).order_by('-event_time')[:30]

    pm_records = work_orders.filter(wo_type='PM')
    repair_records = work_orders.filter(wo_type='REPAIR')
    calibration_records = compliance_records.filter(type__in=['CALIBRATION', 'VERIFICATION'])
    inspection_records = compliance_records.filter(type__in=['INSPECTION', 'SAFETY_TEST'])

    # KPI
    breakdowns_12m = incidents.count()
    from maintenance_app.models import AssetCustodyHistory
    handovers = AssetCustodyHistory.objects.filter(asset=asset).order_by('-handover_at')[:10]

    context = {
        'asset': asset,
        'work_orders': work_orders,
        'incidents': incidents,
        'pm_records': pm_records,
        'repair_records': repair_records,
        'calibration_records': calibration_records,
        'inspection_records': inspection_records,
        'events': events,
        'handovers': handovers,
        'breakdowns_12m': breakdowns_12m,
        'today': date.today(),
    }
    return render(request, 'assets/detail.html', context)


def asset_edit(request, pk):
    tenant = get_default_tenant()
    asset = get_object_or_404(Asset, pk=pk, tenant=tenant, is_deleted=False)

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset, tenant=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật thiết bị {asset.asset_code}!')
            return redirect('asset_detail', pk=asset.pk)
    else:
        form = AssetForm(instance=asset, tenant=tenant)

    context = {
        'form': form,
        'asset': asset,
        'page_title': f'Chỉnh sửa – {asset.asset_code}',
    }
    return render(request, 'assets/add.html', context)


def asset_delete(request, pk):
    tenant = get_default_tenant()
    asset = get_object_or_404(Asset, pk=pk, tenant=tenant)
    if request.method == 'POST':
        asset.is_deleted = True
        asset.save()
        messages.success(request, f'Đã vô hiệu hóa thiết bị {asset.asset_code}.')
        return redirect('asset_list')
    return render(request, 'assets/confirm_delete.html', {'asset': asset})
