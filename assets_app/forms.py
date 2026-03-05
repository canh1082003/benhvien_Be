from django import forms
from .models import Asset, AssetCategory, AssetModel, Manufacturer, Vendor
from locations_app.models import Department, Location


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_code', 'asset_name', 'asset_type',
            'serial_no', 'imei', 'barcode',
            'category', 'model', 'manufacturer', 'vendor',
            'model_name_manual', 'year_of_manufacture', 'risk_class', 'criticality', 'is_portable',
            'owner_dept', 'custodian_user', 'current_location', 'current_status',
            'building', 'floor', 'room', 'bed', 'ops_note',
            'inspection_required', 'inspection_last_date', 'inspection_expiry_date',
            'pm_required', 'pm_last_date', 'pm_next_due_date',
            'commissioned_at', 'useful_life_years',
            'warranty_start_at', 'warranty_end_at',
            'service_contract_id', 'contract_end',
            'notes',
        ]
        widgets = {
            'asset_code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: TB-ICU-2026-00001'}),
            'asset_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Máy theo dõi đa thông số'}),
            'asset_type': forms.Select(attrs={'class': 'select'}),
            'serial_no': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: SN12345'}),
            'imei': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: 3569xxxxxxxxxxxxx'}),
            'barcode': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: QR-0000123'}),
            'category': forms.Select(attrs={'class': 'select'}),
            'model': forms.Select(attrs={'class': 'select'}),
            'manufacturer': forms.Select(attrs={'class': 'select'}),
            'vendor': forms.Select(attrs={'class': 'select'}),
            'model_name_manual': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: IntelliVue MX450'}),
            'year_of_manufacture': forms.NumberInput(attrs={'class': 'input', 'min': 1990, 'max': 2100}),
            'risk_class': forms.Select(attrs={'class': 'select'}),
            'criticality': forms.Select(attrs={'class': 'select'}),
            'owner_dept': forms.Select(attrs={'class': 'select'}),
            'custodian_user': forms.Select(attrs={'class': 'select'}),
            'current_location': forms.Select(attrs={'class': 'select'}),
            'current_status': forms.Select(attrs={'class': 'select'}),
            'building': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Tòa A'}),
            'floor': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Tầng 2'}),
            'room': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Phòng 203'}),
            'bed': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Bed 12'}),
            'ops_note': forms.TextInput(attrs={'class': 'input'}),
            'inspection_required': forms.Select(attrs={'class': 'select'}, choices=[(True, 'Có'), (False, 'Không')]),
            'inspection_last_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'inspection_expiry_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'pm_required': forms.Select(attrs={'class': 'select'}, choices=[(True, 'Có'), (False, 'Không')]),
            'pm_last_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'pm_next_due_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'commissioned_at': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'input', 'min': 1, 'max': 30}),
            'warranty_start_at': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'warranty_end_at': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'service_contract_id': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: SC-2026-0012'}),
            'contract_end': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['category'].queryset = AssetCategory.objects.filter(tenant=tenant, is_deleted=False)
            self.fields['model'].queryset = AssetModel.objects.filter(tenant=tenant, is_deleted=False)
            self.fields['manufacturer'].queryset = Manufacturer.objects.filter(tenant=tenant, is_deleted=False)
            self.fields['vendor'].queryset = Vendor.objects.filter(tenant=tenant, is_deleted=False)
            self.fields['owner_dept'].queryset = Department.objects.filter(tenant=tenant, is_deleted=False)
            self.fields['current_location'].queryset = Location.objects.filter(tenant=tenant, is_deleted=False)
        # Make optional fields not required
        for field_name in ['serial_no', 'imei', 'barcode', 'model', 'manufacturer', 'vendor',
                           'model_name_manual', 'year_of_manufacture', 'risk_class',
                           'owner_dept', 'custodian_user', 'current_location',
                           'building', 'floor', 'room', 'bed', 'ops_note',
                           'inspection_last_date', 'inspection_expiry_date',
                           'pm_last_date', 'pm_next_due_date',
                           'commissioned_at', 'warranty_start_at', 'warranty_end_at',
                           'service_contract_id', 'contract_end', 'notes']:
            if field_name in self.fields:
                self.fields[field_name].required = False
