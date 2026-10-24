from django import forms
from django.core.exceptions import ValidationError
from .models import Shipment, Warehouse, InventoryItem, Vehicle


class ShipmentDispatchForm(forms.ModelForm):
    """
    [US-02, US-03, US-04, BR-02, BR-03, BR-04]
    Production dispatch order form for manifesting and executing outbound cargo movements.
    Enforces deterministic inventory deductions and vehicle operational safety checks.
    """
    STATUS_CHOICES = [
        (Shipment.STATUS_DISPATCHED, 'Immediate Outbound Dispatch (Enforces & Decrements Stock)'),
        (Shipment.STATUS_PENDING, 'Stage as Pending Manifest (Hold Stock)'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        initial=Shipment.STATUS_DISPATCHED,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_status'}),
        help_text="Immediate dispatch requires sufficient stock and marks vehicle as in-transit."
    )

    class Meta:
        model = Shipment
        fields = [
            'origin_warehouse',
            'destination_address',
            'item',
            'quantity',
            'vehicle',
            'driver_name',
            'status',
            'estimated_delivery_date',
        ]
        widgets = {
            'origin_warehouse': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_origin_warehouse',
            }),
            'destination_address': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_destination_address',
                'rows': 2,
                'placeholder': 'e.g., Plot #42/B, Industrial Sector-62, Noida (U.P.) - 201309',
            }),
            'item': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_item',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_quantity',
                'min': '1',
                'value': '1',
            }),
            'vehicle': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_vehicle',
            }),
            'driver_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_driver_name',
                'placeholder': 'e.g., Rajesh Sharma',
            }),
            'estimated_delivery_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'id': 'id_estimated_delivery_date',
                'type': 'datetime-local',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['origin_warehouse'].empty_label = "-- Select Origin Warehouse Depot --"
        self.fields['item'].empty_label = "-- Select SKU / Product --"
        self.fields['vehicle'].empty_label = "-- Select Transport Vehicle (Optional) --"
        self.fields['vehicle'].required = False
        self.fields['driver_name'].required = False
        self.fields['estimated_delivery_date'].required = False

        # Enhance SKU label display with warehouse and live stock quantity
        self.fields['item'].queryset = InventoryItem.objects.select_related('warehouse').order_by('warehouse__code', 'name')
        self.fields['item'].label_from_instance = lambda obj: (
            f"[{obj.warehouse.code}] {obj.name} ({obj.sku}) - Available: {obj.quantity} {obj.unit}"
        )

        # Enhance vehicle label display with maintenance flag
        self.fields['vehicle'].queryset = Vehicle.objects.all().order_by('status', 'registration_number')
        self.fields['vehicle'].label_from_instance = lambda obj: (
            f"{obj.registration_number} ({obj.get_vehicle_type_display()} | Cap: {obj.capacity}kg) "
            f"[{'LOCKED: MAINTENANCE' if obj.status == Vehicle.STATUS_MAINTENANCE else obj.get_status_display()}]"
        )

    def clean(self):
        """
        Enforce deterministic business rules across interrelated form inputs.
        """
        cleaned_data = super().clean()
        origin_warehouse = cleaned_data.get('origin_warehouse')
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        vehicle = cleaned_data.get('vehicle')
        status = cleaned_data.get('status')

        # BR-02: Origin warehouse depot must own the selected SKU
        if origin_warehouse and item:
            if item.warehouse_id != origin_warehouse.id:
                self.add_error(
                    'item',
                    f"[BR-02 Depot Mismatch] SKU '{item.sku}' is housed at '{item.warehouse.name}' ({item.warehouse.code}), "
                    f"not at selected origin '{origin_warehouse.name}' ({origin_warehouse.code})."
                )

        # BR-07: Positive quantity invariant
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', "[BR-07 Data Quality] Shipment quantity must be at least 1 unit.")

        # BR-03: Stock deficit prevention on active dispatch
        if item and quantity is not None and status in [Shipment.STATUS_DISPATCHED, Shipment.STATUS_IN_TRANSIT]:
            if quantity > item.quantity:
                self.add_error(
                    'quantity',
                    f"[BR-03 Stock Deficit] Requested quantity ({quantity}) exceeds available inventory "
                    f"({item.quantity} {item.unit}) for SKU {item.sku}."
                )

        # BR-04: Inoperable vehicle lockout
        if vehicle and status in [Shipment.STATUS_DISPATCHED, Shipment.STATUS_IN_TRANSIT]:
            if vehicle.status == Vehicle.STATUS_MAINTENANCE:
                self.add_error(
                    'vehicle',
                    f"[BR-04 Vehicle Lockout] Vehicle {vehicle.registration_number} is currently UNDER MAINTENANCE "
                    f"and cannot be assigned to an active trip."
                )

        return cleaned_data
