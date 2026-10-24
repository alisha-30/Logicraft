from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint


class LogisticsModelTests(TestCase):
    def setUp(self):
        self.wh = Warehouse.objects.create(
            code="WH-TEST-01",
            name="Test Warehouse",
            address="123 Test St",
            capacity_sqft=10000
        )
        self.item = InventoryItem.objects.create(
            warehouse=self.wh,
            sku="SKU-TEST-01",
            name="Test Solar Battery",
            category="Energy",
            quantity=25,
            unit="units"
        )
        self.vehicle_avail = Vehicle.objects.create(
            registration_number="TEST-DL-01",
            vehicle_type=Vehicle.TYPE_TRUCK,
            capacity=3000,
            status=Vehicle.STATUS_AVAILABLE
        )
        self.vehicle_maint = Vehicle.objects.create(
            registration_number="TEST-DL-02",
            vehicle_type=Vehicle.TYPE_TRUCK,
            capacity=3000,
            status=Vehicle.STATUS_MAINTENANCE
        )

    def test_tc03_reject_vehicle_in_maintenance_on_dispatch(self):
        """[TC-03] Vehicle in Maintenance cannot be assigned to an active dispatched shipment."""
        shipment = Shipment(
            origin_warehouse=self.wh,
            destination_address="456 Destination Rd",
            item=self.item,
            quantity=2,
            vehicle=self.vehicle_maint,
            status=Shipment.STATUS_DISPATCHED
        )
        with self.assertRaises(ValidationError):
            shipment.full_clean()

    def test_tc04_public_tracking_view(self):
        """[TC-04] Public shipment tracking query tests."""
        shipment = Shipment.objects.create(
            origin_warehouse=self.wh,
            destination_address="456 Destination Rd",
            item=self.item,
            quantity=2,
            vehicle=self.vehicle_avail,
            status=Shipment.STATUS_IN_TRANSIT
        )
        ShipmentCheckpoint.objects.create(
            shipment=shipment,
            location_name="Origin Hub",
            status_note="Dispatched"
        )

        client = Client()

        # Valid tracking code
        response = client.get(reverse('track_shipment'), {'q': shipment.tracking_number})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, shipment.tracking_number)
        self.assertContains(response, "Origin Hub")

        # Invalid tracking code
        response_invalid = client.get(reverse('track_shipment'), {'q': 'NON-EXISTENT-CODE'})
        self.assertEqual(response_invalid.status_code, 200)
        self.assertContains(response_invalid, "Tracking Number Not Found")

    def test_tc06_inventory_quantity_tracking(self):
        """[TC-06] Verify warehouse stock updates correctly."""
        initial_qty = self.item.quantity
        self.item.quantity += 15  # Restock action
        self.item.save()
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, initial_qty + 15)
