from django.contrib import admin
from .models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'address', 'capacity_sqft', 'created_at')
    search_fields = ('code', 'name', 'address')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'warehouse', 'category', 'quantity', 'unit', 'updated_at')
    list_filter = ('warehouse', 'category')
    search_fields = ('sku', 'name')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'vehicle_type', 'capacity', 'status', 'updated_at')
    list_filter = ('vehicle_type', 'status')
    search_fields = ('registration_number',)


class ShipmentCheckpointInline(admin.TabularInline):
    model = ShipmentCheckpoint
    extra = 1


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'item', 'quantity', 'origin_warehouse', 'vehicle', 'status', 'created_at')
    list_filter = ('status', 'origin_warehouse')
    search_fields = ('tracking_number', 'destination_address')
    inlines = [ShipmentCheckpointInline]


@admin.register(ShipmentCheckpoint)
class ShipmentCheckpointAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'location_name', 'status_note', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('shipment__tracking_number', 'location_name')
