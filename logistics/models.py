from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Warehouse(models.Model):
    """
    [TR-02] Storage facilities holding stock.
    """
    code = models.CharField(max_length=20, unique=True, help_text="e.g. WH-NORTH-01")
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    capacity_sqft = models.PositiveIntegerField(help_text="Storage floor capacity in sq ft")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class InventoryItem(models.Model):
    """
    [TR-02, US-02] Physical goods stock stored at a specific warehouse.
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_items')
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0, help_text="Quantity on hand")
    unit = models.CharField(max_length=20, default="units", help_text="e.g. boxes, pallets, units")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku}) - {self.quantity} {self.unit} at {self.warehouse.code}"


class Vehicle(models.Model):
    """
    [TR-02, US-04] Fleet vehicles for cargo shipping or passenger transit.
    """
    TYPE_TRUCK = 'TRUCK'
    TYPE_VAN = 'VAN'
    TYPE_BUS = 'BUS'
    VEHICLE_TYPE_CHOICES = [
        (TYPE_TRUCK, 'Cargo Truck'),
        (TYPE_VAN, 'Delivery Van'),
        (TYPE_BUS, 'Transit Bus'),
    ]

    STATUS_AVAILABLE = 'AVAILABLE'
    STATUS_IN_TRANSIT = 'IN_TRANSIT'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_MAINTENANCE, 'Under Maintenance'),
    ]

    registration_number = models.CharField(max_length=20, unique=True, help_text="e.g. DL-01-AB-1234")
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES, default=TYPE_TRUCK)
    capacity = models.PositiveIntegerField(help_text="Cargo payload (kg) or passenger seat capacity")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    notes = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_vehicle_type_display()}] {self.registration_number} - {self.get_status_display()}"


def generate_tracking_number():
    """
    [BR-05] Generates a unique, deterministic-pattern tracking code.
    Format: LC-TRK-YYYYMMDD-XXXX
    """
    today = timezone.now().strftime('%Y%m%d')
    suffix = uuid.uuid4().hex[:6].upper()
    return f"LC-TRK-{today}-{suffix}"


class Shipment(models.Model):
    """
    [TR-02, US-01, BR-01] Cargo delivery orders and state lifecycle.
    """
    STATUS_PENDING = 'PENDING'
    STATUS_DISPATCHED = 'DISPATCHED'
    STATUS_IN_TRANSIT = 'IN_TRANSIT'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_DISPATCHED, 'Dispatched'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    tracking_number = models.CharField(
        max_length=32,
        unique=True,
        default=generate_tracking_number,
        editable=False,
        help_text="Unique tracking identifier"
    )
    origin_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='shipments_origin')
    destination_address = models.CharField(max_length=255)
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='shipments')
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity to ship")
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_shipments',
        help_text="Vehicle assigned to this cargo"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    driver_name = models.CharField(max_length=100, blank=True, default="", help_text="Assigned driver name")
    estimated_delivery_date = models.DateTimeField(null=True, blank=True, help_text="Estimated delivery timestamp")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        [BR-01, BR-02, BR-03, BR-04] Deterministic business rules validation.
        """
        super().clean()

        # Safe attribute resolution to guard against ModelForm post_clean unassigned fields
        try:
            vehicle = self.vehicle
        except (Vehicle.DoesNotExist, AttributeError):
            vehicle = None

        try:
            item = self.item
        except (InventoryItem.DoesNotExist, AttributeError):
            item = None

        try:
            origin_wh = self.origin_warehouse
        except (Warehouse.DoesNotExist, AttributeError):
            origin_wh = None

        # BR-04: Vehicle must be available if assigned during dispatch
        if vehicle and self.status in [self.STATUS_DISPATCHED, self.STATUS_IN_TRANSIT]:
            if vehicle.status == Vehicle.STATUS_MAINTENANCE:
                raise ValidationError({"vehicle": f"Vehicle {vehicle.registration_number} is under maintenance and cannot be assigned."})

        # BR-02: Ensure origin warehouse matches item warehouse
        if item and origin_wh and item.warehouse_id != origin_wh.id:
            raise ValidationError({"item": f"Item {item.name} is stored at {item.warehouse}, not at origin warehouse {origin_wh}."})

        # BR-03: Prevent dispatching more than available warehouse stock
        if item and self.quantity is not None and self.status in [self.STATUS_DISPATCHED, self.STATUS_IN_TRANSIT]:
            if self.quantity > item.quantity:
                raise ValidationError({"quantity": f"Requested quantity ({self.quantity}) exceeds available stock ({item.quantity} units) for SKU {item.sku}."})

    def __str__(self):
        return f"{self.tracking_number} | {self.item.name} ({self.quantity}) -> {self.get_status_display()}"


class ShipmentCheckpoint(models.Model):
    """
    [TR-02, US-03, TC-04] Audit trail of package transit progress.
    """
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='checkpoints')
    location_name = models.CharField(max_length=120, help_text="e.g. Central Sorting Hub, Delhi")
    status_note = models.CharField(max_length=255, help_text="e.g. Package arrived at sorting center")
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.location_name} - {self.status_note}"
