from rest_framework import serializers
from assets_app.models import Asset, AssetCategory, Manufacturer, Vendor
from locations_app.models import Department, Location
from core.models import Tenant


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'country']


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'phone', 'email']


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ['id', 'code', 'name']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name']


class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for asset list page."""
    category_name = serializers.CharField(source='category.name', default='', read_only=True)
    owner_dept_name = serializers.CharField(source='owner_dept.name', default='', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', default='', read_only=True)

    # Computed status fields
    inspection_status = serializers.SerializerMethodField()
    pm_status = serializers.SerializerMethodField()
    eol_status = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id', 'asset_code', 'asset_name', 'serial_no', 'barcode', 'imei',
            'current_status', 'status_badge',
            'category_name', 'owner_dept_name', 'manufacturer_name',
            'building', 'floor', 'room', 'risk_class', 'criticality',
            'inspection_required', 'inspection_expiry_date',
            'pm_required', 'pm_next_due_date',
            'commissioned_at', 'useful_life_years',
            'warranty_end_at', 'updated_at',
            'inspection_status', 'pm_status', 'eol_status',
        ]

    def get_status_badge(self, obj):
        return obj.get_status_badge_class()

    def get_inspection_status(self, obj):
        status, text, badge = obj.inspection_status()
        return {'status': status, 'text': text, 'badge': badge}

    def get_pm_status(self, obj):
        status, text, badge = obj.pm_status()
        return {'status': status, 'text': text, 'badge': badge}

    def get_eol_status(self, obj):
        status, text, badge = obj.eol_status()
        return {'status': status, 'text': text, 'badge': badge}


class AssetDetailSerializer(AssetListSerializer):
    """Full serializer for asset detail/create/update."""
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetCategory.objects.all(),
        source='category', write_only=True, required=False, allow_null=True
    )
    owner_dept = DepartmentSerializer(read_only=True)
    owner_dept_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='owner_dept', write_only=True, required=False, allow_null=True
    )
    manufacturer = ManufacturerSerializer(read_only=True)
    manufacturer_id = serializers.PrimaryKeyRelatedField(
        queryset=Manufacturer.objects.all(),
        source='manufacturer', write_only=True, required=False, allow_null=True
    )
    vendor = VendorSerializer(read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        source='vendor', write_only=True, required=False, allow_null=True
    )

    class Meta(AssetListSerializer.Meta):
        fields = AssetListSerializer.Meta.fields + [
            'category', 'category_id',
            'owner_dept', 'owner_dept_id',
            'manufacturer', 'manufacturer_id',
            'vendor', 'vendor_id',
            'asset_type', 'model_name_manual', 'purchase_price', 'purchase_at',
            'warranty_start_at', 'inspection_last_date', 'pm_last_date',
            'pm_interval_months', 'notes', 'created_at',
        ]
