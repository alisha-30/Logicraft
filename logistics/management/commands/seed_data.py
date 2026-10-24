from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from logistics.models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint
from transit.models import TransitRoute, TransitSchedule, TicketBooking


class Command(BaseCommand):
    help = "Seeds initial demo data for LogiCraft (warehouses, fleet, shipments, transit routes)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding LogiCraft demo data...")

        # 1. Warehouses
        wh1, _ = Warehouse.objects.get_or_create(
            code="WH-DEL-01",
            defaults={"name": "Northern Regional Depot", "address": "Okhla Phase III, New Delhi", "capacity_sqft": 45000}
        )
        wh2, _ = Warehouse.objects.get_or_create(
            code="WH-MUM-01",
            defaults={"name": "Western Coastal Hub", "address": "Bhiwandi Logistics Park, Mumbai", "capacity_sqft": 60000}
        )
        wh3, _ = Warehouse.objects.get_or_create(
            code="WH-BLR-01",
            defaults={"name": "Southern Tech Distribution", "address": "Peenya Industrial Area, Bengaluru", "capacity_sqft": 35000}
        )

        # 2. Inventory Items
        item1, _ = InventoryItem.objects.get_or_create(
            sku="SKU-SOL-101",
            defaults={"warehouse": wh1, "name": "5kVA Solar Inverter", "category": "Renewable Energy", "quantity": 45, "unit": "units"}
        )
        item2, _ = InventoryItem.objects.get_or_create(
            sku="SKU-MED-202",
            defaults={"warehouse": wh1, "name": "Emergency Medical Kit", "category": "Healthcare", "quantity": 120, "unit": "boxes"}
        )
        item3, _ = InventoryItem.objects.get_or_create(
            sku="SKU-BAT-303",
            defaults={"warehouse": wh2, "name": "Lithium Battery Pack (100Ah)", "category": "Electronics", "quantity": 80, "unit": "units"}
        )
        item4, _ = InventoryItem.objects.get_or_create(
            sku="SKU-WTR-404",
            defaults={"warehouse": wh3, "name": "Water Purification Filter", "category": "Sanitation", "quantity": 250, "unit": "filters"}
        )

        # 3. Fleet Vehicles
        v_truck1, _ = Vehicle.objects.get_or_create(
            registration_number="DL-01-TR-9021",
            defaults={"vehicle_type": Vehicle.TYPE_TRUCK, "capacity": 5000, "status": Vehicle.STATUS_AVAILABLE, "notes": "Heavy hauler, recently serviced"}
        )
        v_van1, _ = Vehicle.objects.get_or_create(
            registration_number="MH-02-VN-4412",
            defaults={"vehicle_type": Vehicle.TYPE_VAN, "capacity": 1500, "status": Vehicle.STATUS_AVAILABLE, "notes": "Local city delivery van"}
        )
        v_maint, _ = Vehicle.objects.get_or_create(
            registration_number="DL-01-TR-3399",
            defaults={"vehicle_type": Vehicle.TYPE_TRUCK, "capacity": 8000, "status": Vehicle.STATUS_MAINTENANCE, "notes": "Engine overhaul in progress [BR-03 test]"}
        )
        v_bus1, _ = Vehicle.objects.get_or_create(
            registration_number="KA-05-BS-1100",
            defaults={"vehicle_type": Vehicle.TYPE_BUS, "capacity": 30, "status": Vehicle.STATUS_AVAILABLE, "notes": "30-seater commuter coach"}
        )
        v_bus2, _ = Vehicle.objects.get_or_create(
            registration_number="DL-01-BS-2200",
            defaults={"vehicle_type": Vehicle.TYPE_BUS, "capacity": 25, "status": Vehicle.STATUS_AVAILABLE, "notes": "25-seater airport shuttle"}
        )

        # 4. Shipments with checkpoints
        now = timezone.now()
        if not Shipment.objects.filter(tracking_number="LC-TRK-20261010-DEMO01").exists():
            s1 = Shipment.objects.create(
                tracking_number="LC-TRK-20261010-DEMO01",
                origin_warehouse=wh1,
                destination_address="Sector 62, Noida, Uttar Pradesh",
                item=item1,
                quantity=4,
                vehicle=v_truck1,
                status=Shipment.STATUS_IN_TRANSIT
            )
            ShipmentCheckpoint.objects.create(
                shipment=s1,
                location_name="Northern Regional Depot, Delhi",
                status_note="Cargo picked up and loaded onto vehicle",
                timestamp=now - timedelta(hours=6)
            )
            ShipmentCheckpoint.objects.create(
                shipment=s1,
                location_name="Yamuna Expressway Toll Plaza",
                status_note="In transit through inter-state corridor",
                timestamp=now - timedelta(hours=2)
            )

        if not Shipment.objects.filter(tracking_number="LC-TRK-20261010-DEMO02").exists():
            s2 = Shipment.objects.create(
                tracking_number="LC-TRK-20261010-DEMO02",
                origin_warehouse=wh2,
                destination_address="Andheri East, Mumbai",
                item=item3,
                quantity=10,
                vehicle=v_van1,
                status=Shipment.STATUS_DELIVERED
            )
            ShipmentCheckpoint.objects.create(
                shipment=s2,
                location_name="Western Coastal Hub, Mumbai",
                status_note="Dispatched from warehouse",
                timestamp=now - timedelta(days=1)
            )
            ShipmentCheckpoint.objects.create(
                shipment=s2,
                location_name="Andheri East Sorting Center",
                status_note="Out for delivery",
                timestamp=now - timedelta(hours=5)
            )
            ShipmentCheckpoint.objects.create(
                shipment=s2,
                location_name="Customer Address",
                status_note="Delivered and signature received",
                timestamp=now - timedelta(hours=1)
            )

        # 5. Transit Routes & Schedules
        route1, _ = TransitRoute.objects.get_or_create(
            route_code="ROUTE-101",
            defaults={"origin_stop": "Central Bus Terminal", "destination_stop": "Airport Terminal 3", "duration_minutes": 45}
        )
        route2, _ = TransitRoute.objects.get_or_create(
            route_code="ROUTE-202",
            defaults={"origin_stop": "Metro Interchange Station", "destination_stop": "Tech City Cyber Park", "duration_minutes": 35}
        )

        sched1, _ = TransitSchedule.objects.get_or_create(
            route=route1,
            vehicle=v_bus2,
            defaults={
                "departure_time": now + timedelta(hours=3),
                "arrival_time": now + timedelta(hours=3, minutes=45),
                "fare": 75.00
            }
        )
        sched2, _ = TransitSchedule.objects.get_or_create(
            route=route2,
            vehicle=v_bus1,
            defaults={
                "departure_time": now + timedelta(hours=5),
                "arrival_time": now + timedelta(hours=5, minutes=35),
                "fare": 40.00
            }
        )

        # Seed sample bookings for sched1
        if sched1.bookings.count() == 0:
            TicketBooking.objects.create(
                schedule=sched1,
                passenger_name="Aarav Mehta",
                passenger_email="aarav@example.com",
                seat_number=1,
                status=TicketBooking.STATUS_CONFIRMED
            )
            TicketBooking.objects.create(
                schedule=sched1,
                passenger_name="Pooja Verma",
                passenger_email="pooja@example.com",
                seat_number=2,
                status=TicketBooking.STATUS_CONFIRMED
            )

        self.stdout.write(self.style.SUCCESS("LogiCraft demo data successfully seeded!"))
