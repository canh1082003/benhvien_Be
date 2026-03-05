from datetime import date
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

from assets_app.models import Asset, AssetCategory, Manufacturer, Vendor
from locations_app.models import Department
from core.models import Tenant
from .serializers import (
    AssetListSerializer, AssetDetailSerializer,
    AssetCategorySerializer, DepartmentSerializer,
    ManufacturerSerializer, VendorSerializer,
)


def get_default_tenant():
    return Tenant.objects.first()


class AssetViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['asset_code', 'asset_name', 'serial_no', 'imei', 'barcode']
    ordering_fields = ['asset_code', 'asset_name', 'current_status', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        tenant = get_default_tenant()
        qs = Asset.objects.filter(tenant=tenant, is_deleted=False).select_related(
            'category', 'owner_dept', 'manufacturer', 'vendor'
        )
        # Filters from query params
        status = self.request.query_params.get('status')
        dept = self.request.query_params.get('dept')
        category = self.request.query_params.get('category')
        quick = self.request.query_params.get('quick')

        if status:
            qs = qs.filter(current_status=status)
        if dept:
            qs = qs.filter(owner_dept_id=dept)
        if category:
            qs = qs.filter(category_id=category)

        today = date.today()
        if quick == 'inspection_overdue':
            qs = qs.filter(inspection_required=True, inspection_expiry_date__lt=today)
        elif quick == 'inspection_soon':
            from datetime import timedelta
            qs = qs.filter(inspection_required=True,
                           inspection_expiry_date__gte=today,
                           inspection_expiry_date__lte=today + timedelta(days=30))
        elif quick == 'pm_overdue':
            qs = qs.filter(pm_required=True, pm_next_due_date__lt=today)
        elif quick == 'pm_soon':
            from datetime import timedelta
            qs = qs.filter(pm_required=True,
                           pm_next_due_date__gte=today,
                           pm_next_due_date__lte=today + timedelta(days=30))
        elif quick == 'breakdown':
            qs = qs.filter(current_status='BREAKDOWN')

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetDetailSerializer

    def perform_create(self, serializer):
        tenant = get_default_tenant()
        serializer.save(tenant=tenant)

    @action(detail=False, methods=['get'])
    def kpi(self, request):
        tenant = get_default_tenant()
        today = date.today()
        from datetime import timedelta
        qs = Asset.objects.filter(tenant=tenant, is_deleted=False)
        return Response({
            'total': qs.count(),
            'in_service': qs.filter(current_status='IN_SERVICE').count(),
            'standby': qs.filter(current_status='STANDBY').count(),
            'under_maintenance': qs.filter(current_status='UNDER_MAINTENANCE').count(),
            'breakdown': qs.filter(current_status='BREAKDOWN').count(),
            'out_of_service': qs.filter(current_status='OUT_OF_SERVICE').count(),
            'inspection_overdue': qs.filter(inspection_required=True, inspection_expiry_date__lt=today).count(),
            'inspection_soon': qs.filter(
                inspection_required=True,
                inspection_expiry_date__gte=today,
                inspection_expiry_date__lte=today + timedelta(days=30)
            ).count(),
            'pm_overdue': qs.filter(pm_required=True, pm_next_due_date__lt=today).count(),
            'pm_soon': qs.filter(
                pm_required=True,
                pm_next_due_date__gte=today,
                pm_next_due_date__lte=today + timedelta(days=30)
            ).count(),
        })


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        tenant = get_default_tenant()
        return Department.objects.filter(tenant=tenant, is_deleted=False)


class AssetCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssetCategorySerializer

    def get_queryset(self):
        tenant = get_default_tenant()
        return AssetCategory.objects.filter(tenant=tenant)


class ManufacturerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ManufacturerSerializer

    def get_queryset(self):
        tenant = get_default_tenant()
        return Manufacturer.objects.filter(tenant=tenant)


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VendorSerializer

    def get_queryset(self):
        tenant = get_default_tenant()
        return Vendor.objects.filter(tenant=tenant)


def admin_bridge_view(request):
    token = request.GET.get('token')
    if not token:
        return redirect('http://localhost:5173/login')
    
    try:
        # Verify token
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        
        # Log in to Django session
        if user.is_staff:
            login(request, user)
            return redirect('/admin/')
        else:
            return redirect('http://localhost:5173/?error=not_staff')
            
    except Exception:
        return redirect('http://localhost:5173/login')
