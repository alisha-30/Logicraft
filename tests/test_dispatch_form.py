from django.test import TestCase, Client
from django.urls import reverse
from logistics.models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint


class ShipmentDispatchFormTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.wh_delhi = Warehouse.objects.create(
            code="WH-DEL-01",
            name="Delhi Regional Hub",
            address="Plot 10, Okhla Phase 1, New Delhi",
            capacity_sqft=25000
        )
        self.wh_mumbai = Warehouse.objects.create(
            code="WH-MUM-01",
            name="Mumbai Coastal Depot",
            address="Plot 88, Nhava Sheva, Navi Mumbai",
            capacity_sqft=30000
        )

        self.item_solar = InventoryItem.objects.create(
            warehouse=self.wh_delhi,
            sku="SKU-SOL-101",
            name="5kVA Solar Inverter",
            category="Energy",
            quantity=50,
            unit="units"
        )
        self.item_low_stock = InventoryItem.objects.create(
            warehouse=self.wh_delhi,
            sku="SKU-CRIT-001",
            name="Critical Spare Kit",
            category="Spares",
            quantity=3,
            unit="kits"
        )

        self.truck_available = Vehicle.objects.create(
            registration_number="DL-01-TR-1000",
            vehicle_type=Vehicle.TYPE_TRUCK,
            capacity=5000,
            status=Vehicle.STATUS_AVAILABLE
        )
        self.truck_maintenance = Vehicle.objects.create(
            registration_number="DL-01-TR-9999",
            vehicle_type=Vehicle.TYPE_TRUCK,
            capacity=5000,
            status=Vehicle.STATUS_MAINTENANCE
        )

    def test_dispatch_form_view_renders_get(self):
        """Verify GET /shipments/dispatch/ returns 200 and loads grouped fields."""
        response = self.client.get(reverse('shipment_dispatch'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Outbound Shipment Dispatch & Stock Manifest")
        self.assertContains(response, "id_origin_warehouse")
        self.assertContains(response, "id_item")
        self.assertContains(response, "id_quantity")
        self.assertContains(response, "id_vehicle")
        self.assertContains(response, "submitDispatchBtn")
        self.assertContains(response, "itemsData")

    def test_dispatch_successful_decrements_inventory_and_locks_vehicle(self):
        """[US-03, BR-03, TR-02] Successful dispatch transactionally reduces stock and updates vehicle."""
        payload = {
            'origin_warehouse': self.wh_delhi.id,
            'destination_address': 'Sector 62, Electronic City, Noida',
            'item': self.item_solar.id,
            'quantity': 12,
            'vehicle': self.truck_available.id,
            'driver_name': 'Ramesh Kumar',
            'status': Shipment.STATUS_DISPATCHED,
            'estimated_delivery_date': '2026-10-25T14:00',
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 302)

        # 1. Verify Inventory deducted atomically (50 - 12 = 38)
        self.item_solar.refresh_from_db()
        self.assertEqual(self.item_solar.quantity, 38)

        # 2. Verify Vehicle transitioned to IN_TRANSIT
        self.truck_available.refresh_from_db()
        self.assertEqual(self.truck_available.status, Vehicle.STATUS_IN_TRANSIT)

        # 3. Verify Shipment record created with tracking number
        shipment = Shipment.objects.latest('created_at')
        self.assertEqual(shipment.item, self.item_solar)
        self.assertEqual(shipment.quantity, 12)
        self.assertEqual(shipment.status, Shipment.STATUS_DISPATCHED)
        self.assertTrue(shipment.tracking_number.startswith('LC-TRK-'))

        # 4. Verify initial audit waypoint created
        self.assertEqual(shipment.checkpoints.count(), 1)
        checkpoint = shipment.checkpoints.first()
        self.assertIn("Delhi Regional Hub", checkpoint.location_name)

    def test_dispatch_fails_when_quantity_exceeds_available_stock(self):
        """[BR-03, TR-03] Submitting quantity greater than on-hand stock is rejected and preserves stock."""
        initial_stock = self.item_low_stock.quantity  # 3 units
        payload = {
            'origin_warehouse': self.wh_delhi.id,
            'destination_address': 'Consignee Hub B, Gurgaon',
            'item': self.item_low_stock.id,
            'quantity': 10,  # Exceeds 3 units!
            'vehicle': self.truck_available.id,
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[BR-03 Stock Deficit]")

        # Ensure stock remained completely untouched
        self.item_low_stock.refresh_from_db()
        self.assertEqual(self.item_low_stock.quantity, initial_stock)
        self.assertEqual(Shipment.objects.filter(item=self.item_low_stock).count(), 0)

    def test_dispatch_fails_when_origin_warehouse_does_not_match_item(self):
        """[BR-02] Mismatch between origin warehouse and item depot is rejected."""
        payload = {
            'origin_warehouse': self.wh_mumbai.id,  # Mumbai selected, but item is in Delhi!
            'destination_address': 'Navi Mumbai Port Area',
            'item': self.item_solar.id,
            'quantity': 5,
            'vehicle': self.truck_available.id,
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[BR-02 Depot Mismatch]")
        self.assertEqual(Shipment.objects.count(), 0)

    def test_dispatch_fails_when_assigning_maintenance_vehicle(self):
        """[BR-04, TR-04] Inoperable vehicle undergoing maintenance cannot be dispatched."""
        payload = {
            'origin_warehouse': self.wh_delhi.id,
            'destination_address': 'Connaught Place, New Delhi',
            'item': self.item_solar.id,
            'quantity': 2,
            'vehicle': self.truck_maintenance.id,  # Status is MAINTENANCE!
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[BR-04 Vehicle Lockout]")
        self.assertEqual(Shipment.objects.count(), 0)

    def test_dispatch_fails_on_zero_or_negative_quantity(self):
        """[BR-07, TR-07] Non-positive quantities are strictly rejected."""
        payload = {
            'origin_warehouse': self.wh_delhi.id,
            'destination_address': 'Connaught Place, New Delhi',
            'item': self.item_solar.id,
            'quantity': 0,
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "must be at least 1 unit")

    def test_pending_manifest_does_not_prematurely_decrement_stock(self):
        """Staging a shipment as PENDING does not immediately decrement warehouse inventory."""
        payload = {
            'origin_warehouse': self.wh_delhi.id,
            'destination_address': 'Buffer Depot, Faridabad',
            'item': self.item_solar.id,
            'quantity': 5,
            'status': Shipment.STATUS_PENDING,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 302)

        # Inventory remains untouched at 50 units
        self.item_solar.refresh_from_db()
        self.assertEqual(self.item_solar.quantity, 50)

        shipment = Shipment.objects.latest('created_at')
        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)
