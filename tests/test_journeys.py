"""
LogiCraft: End-to-End User Journey & Resiliency Test Suite
===========================================================
Verifies complete cross-subsystem workflows from interface to database:
1. Dispatcher Cargo Lifecycle Journey (Auth -> Dispatch -> Decrement -> Track -> Dashboard)
2. Commuter Transit & Ticketing Journey (Search -> Seat Availability -> Book -> Capacity Saturation Guard)
3. Edge Cases, Failure Resiliency & Security Audits (BR-03, BR-04, BR-06, BR-07, BR-08)
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from logistics.models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint
from transit.models import TransitRoute, TransitSchedule, TicketBooking


class DispatcherCargoLifecycleJourneyTests(TestCase):
    """
    User Journey 1: Outbound Freight Dispatch & Public Tracking Lifecycle
    Actors: Operations Director, Fleet Dispatcher, Consignee (Public)
    Stories: US-01, US-02, US-03, US-04, US-05
    Rules: BR-01, BR-02, BR-03, BR-04, BR-05, TR-02, TR-03
    """

    def setUp(self):
        self.client = Client()

        # Seed staff user account
        self.dispatcher_user = User.objects.create_user(
            username='dispatcher_vikram',
            email='vikram.dispatcher@example.com',
            password='SecurePassword123',
            is_staff=True
        )

        # Seed physical warehouse depot
        self.depot_delhi = Warehouse.objects.create(
            code="WH-DEL-01",
            name="Northern Regional Hub - Delhi",
            address="Plot #12, Okhla Industrial Area Phase-III, New Delhi",
            capacity_sqft=45000
        )

        # Seed inventory stock: 100 units of solar batteries
        self.item_battery = InventoryItem.objects.create(
            warehouse=self.depot_delhi,
            sku="SKU-BATT-900",
            name="Lithium Phosphate 48V Battery Pack",
            category="Energy Storage",
            quantity=100,
            unit="units"
        )

        # Seed available freight transport vehicle
        self.truck_available = Vehicle.objects.create(
            registration_number="DL-01-TR-5520",
            vehicle_type=Vehicle.TYPE_TRUCK,
            capacity=7500,
            status=Vehicle.STATUS_AVAILABLE
        )

    def test_complete_outbound_dispatch_to_public_tracking_journey(self):
        """
        Step 1: Dispatcher logs into staff workspace.
        Step 2: Operations dashboard shows baseline stats (0 active shipments, 100 units).
        Step 3: Dispatcher navigates to dispatch form and verifies initial available stock.
        Step 4: Dispatcher manifests an order for 25 units.
        Step 5: System atomically reduces stock to 75, sets vehicle to IN_TRANSIT, and logs waypoint.
        Step 6: Consignee queries public tracking page using new tracking number and views stepper.
        Step 7: Operations Director refreshes dashboard and sees active shipments incremented.
        """
        # Step 1: Staff authentication
        login_res = self.client.post(reverse('login'), {
            'username': 'dispatcher_vikram',
            'password': 'SecurePassword123'
        }, follow=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertContains(login_res, "Welcome back, dispatcher_vikram!")

        # Step 2: Dashboard baseline inspection (BR-01)
        dash_initial = self.client.get(reverse('home'))
        self.assertEqual(dash_initial.status_code, 200)
        self.assertEqual(dash_initial.context['stats']['shipments_active'], 0)
        self.assertEqual(dash_initial.context['stats']['total_inventory_units'], 100)
        self.assertEqual(dash_initial.context['stats']['vehicles_available'], 1)
        self.assertEqual(dash_initial.context['stats']['vehicles_in_transit'], 0)

        # Step 3: Dispatch form inspection (US-03)
        dispatch_page = self.client.get(reverse('shipment_dispatch'))
        self.assertEqual(dispatch_page.status_code, 200)
        self.assertContains(dispatch_page, "Create Outbound Dispatch Order")
        self.assertContains(dispatch_page, "SKU-BATT-900")

        # Step 4: Submit valid shipment dispatch manifest (US-03, BR-03, BR-04)
        payload = {
            'origin_warehouse': self.depot_delhi.id,
            'destination_address': 'Plot #42/B, Industrial Sector-62, Noida (U.P.) - 201309',
            'item': self.item_battery.id,
            'quantity': 25,
            'vehicle': self.truck_available.id,
            'driver_name': 'Ramesh Kumar',
            'status': Shipment.STATUS_DISPATCHED,
            'estimated_delivery_date': '2026-10-25T18:00',
        }
        dispatch_res = self.client.post(reverse('shipment_dispatch'), payload)

        # Step 5: Assert redirection to tracking screen
        self.assertEqual(dispatch_res.status_code, 302)
        redirect_url = dispatch_res.url
        self.assertIn('/track/?q=LC-TRK-', redirect_url)

        # Verify Database Atomic Transactions:
        # A. Inventory decremented by 25 (100 -> 75)
        self.item_battery.refresh_from_db()
        self.assertEqual(self.item_battery.quantity, 75)

        # B. Vehicle status changed to IN_TRANSIT
        self.truck_available.refresh_from_db()
        self.assertEqual(self.truck_available.status, Vehicle.STATUS_IN_TRANSIT)

        # C. Shipment record manifested with valid tracking number
        shipment = Shipment.objects.latest('created_at')
        self.assertEqual(shipment.item, self.item_battery)
        self.assertEqual(shipment.quantity, 25)
        self.assertEqual(shipment.status, Shipment.STATUS_DISPATCHED)
        self.assertEqual(shipment.driver_name, 'Ramesh Kumar')
        self.assertTrue(shipment.tracking_number.startswith('LC-TRK-'))

        # D. Initial audit waypoint created
        self.assertEqual(shipment.checkpoints.count(), 1)
        checkpoint = shipment.checkpoints.first()
        self.assertIn("Northern Regional Hub - Delhi", checkpoint.location_name)
        self.assertIn("Dispatched", checkpoint.status_note)

        # Step 6: Consignee queries public parcel tracking page (US-05, BR-05)
        tracking_res = self.client.get(reverse('track_shipment'), {'q': shipment.tracking_number})
        self.assertEqual(tracking_res.status_code, 200)
        self.assertContains(tracking_res, shipment.tracking_number)
        self.assertContains(tracking_res, "Northern Regional Hub - Delhi")
        self.assertContains(tracking_res, "Plot #42/B, Industrial Sector-62, Noida")
        self.assertContains(tracking_res, "Ramesh Kumar")
        self.assertContains(tracking_res, "DL-01-TR-5520")

        # Step 7: Operations Director inspects updated dashboard
        dash_updated = self.client.get(reverse('home'))
        self.assertEqual(dash_updated.status_code, 200)
        self.assertEqual(dash_updated.context['stats']['shipments_active'], 1)
        self.assertEqual(dash_updated.context['stats']['total_inventory_units'], 75)
        self.assertEqual(dash_updated.context['stats']['vehicles_available'], 0)
        self.assertEqual(dash_updated.context['stats']['vehicles_in_transit'], 1)


class CommuterTransitTicketingJourneyTests(TestCase):
    """
    User Journey 2: Commuter Timetable Search & Capacity-Guarded Seat Booking
    Actors: Public Commuter
    Stories: US-06
    Rules: BR-06, BR-08, TR-06
    """

    def setUp(self):
        self.client = Client()

        # Seed transit bus vehicle with capacity of 3 seats for fast boundary testing
        self.bus = Vehicle.objects.create(
            registration_number="DL-01-BS-1001",
            vehicle_type=Vehicle.TYPE_BUS,
            capacity=3,
            status=Vehicle.STATUS_AVAILABLE
        )

        # Seed route and departure schedule
        self.route = TransitRoute.objects.create(
            route_code="ROUTE-EXP-101",
            origin_stop="Kashmere Gate ISBT, Delhi",
            destination_stop="Sindhi Camp, Jaipur",
            duration_minutes=300
        )
        now = timezone.now()
        self.schedule = TransitSchedule.objects.create(
            route=self.route,
            vehicle=self.bus,
            departure_time=now + timedelta(hours=4),
            arrival_time=now + timedelta(hours=9),
            fare=450.00
        )

    def test_complete_route_search_and_seat_booking_journey(self):
        """
        Step 1: Commuter searches routes for 'Delhi' to 'Jaipur'.
        Step 2: Timetable shows 3 remaining seats.
        Step 3: Commuter 1 books Seat 1 -> remaining seats become 2.
        Step 4: Commuter 2 books Seat 2 -> remaining seats become 1.
        Step 5: Commuter 3 books Seat 3 -> remaining seats become 0 (Sold Out).
        Step 6: Commuter 4 attempts to book on the same schedule -> System rejects booking (BR-06).
        """
        # Step 1: Timetable search with query parameters
        search_res = self.client.get(reverse('transit_schedules'), {
            'origin': 'Delhi',
            'destination': 'Jaipur'
        })
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, "ROUTE-EXP-101")
        self.assertContains(search_res, "3 seats left")

        # Step 2 & 3: Commuter 1 books Seat 1
        book_res_1 = self.client.post(
            reverse('book_ticket', kwargs={'schedule_id': self.schedule.id}),
            {
                'passenger_name': 'Aarav Sharma',
                'passenger_email': 'aarav.sharma@example.com',
                'seat_number': 1
            }
        )
        self.assertEqual(book_res_1.status_code, 200)
        self.assertContains(book_res_1, "Seat reserved successfully!")
        self.assertContains(book_res_1, "LC-TKT-")

        # Verify seat count: 3 - 1 = 2
        self.assertEqual(self.schedule.remaining_seats(), 2)

        # Step 4: Commuter 2 books Seat 2
        book_res_2 = self.client.post(
            reverse('book_ticket', kwargs={'schedule_id': self.schedule.id}),
            {
                'passenger_name': 'Neha Verma',
                'passenger_email': 'neha.verma@example.com',
                'seat_number': 2
            }
        )
        self.assertEqual(book_res_2.status_code, 200)
        self.assertEqual(self.schedule.remaining_seats(), 1)

        # Step 5: Commuter 3 books the final seat (Seat 3)
        book_res_3 = self.client.post(
            reverse('book_ticket', kwargs={'schedule_id': self.schedule.id}),
            {
                'passenger_name': 'Karan Gupta',
                'passenger_email': 'karan.gupta@example.com',
                'seat_number': 3
            }
        )
        self.assertEqual(book_res_3.status_code, 200)

        # Bus is now 100% capacity saturated: remaining_seats == 0
        self.assertEqual(self.schedule.remaining_seats(), 0)

        # Step 6: Overbooking Guard (BR-06)
        # Commuter 4 attempts to book on the full schedule
        book_res_4 = self.client.post(
            reverse('book_ticket', kwargs={'schedule_id': self.schedule.id}),
            {
                'passenger_name': 'Pooja Iyer',
                'passenger_email': 'pooja.iyer@example.com',
                'seat_number': 1
            },
            follow=True
        )
        # Rejects and redirects to timetable with sold-out alert
        self.assertEqual(book_res_4.status_code, 200)
        self.assertContains(book_res_4, "sold out (0 seats remaining)")

        # Verify confirmed booking count strictly equals capacity (3) and did not exceed
        self.assertEqual(
            TicketBooking.objects.filter(schedule=self.schedule, status=TicketBooking.STATUS_CONFIRMED).count(),
            3
        )


class EdgeCasesAndFailureResilienceJourneyTests(TestCase):
    """
    User Journey 3: Boundary Violations, Missing Records & Security Resiliency
    Rules: BR-02, BR-03, BR-04, BR-07, BR-08, TR-02, TR-03, TR-04
    """

    def setUp(self):
        self.client = Client()

        self.wh_source = Warehouse.objects.create(
            code="WH-SRC-01",
            name="Source Warehouse",
            address="Sector 18, Noida",
            capacity_sqft=10000
        )
        self.wh_other = Warehouse.objects.create(
            code="WH-OTH-02",
            name="Other Warehouse",
            address="Bhiwandi, Mumbai",
            capacity_sqft=15000
        )

        self.item_limited = InventoryItem.objects.create(
            warehouse=self.wh_source,
            sku="SKU-LIM-001",
            name="Precision Sensor",
            category="Electronics",
            quantity=5,
            unit="boxes"
        )

        self.vehicle_maintenance = Vehicle.objects.create(
            registration_number="UP-16-TR-8811",
            vehicle_type=Vehicle.TYPE_TRUCK,
            capacity=4000,
            status=Vehicle.STATUS_MAINTENANCE,
            notes="Engine overhaul in progress"
        )

    def test_over_allocation_stock_deficit_rejection(self):
        """[BR-03, TR-03] Dispatching 20 units when stock is 5 is rejected and preserves inventory."""
        payload = {
            'origin_warehouse': self.wh_source.id,
            'destination_address': 'Client Site C',
            'item': self.item_limited.id,
            'quantity': 20,
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[BR-03 Stock Deficit]")

        # Database inventory remained unchanged
        self.item_limited.refresh_from_db()
        self.assertEqual(self.item_limited.quantity, 5)
        self.assertEqual(Shipment.objects.count(), 0)

    def test_maintenance_vehicle_lockout_rejection(self):
        """[BR-04, TR-04] Assigning a vehicle in MAINTENANCE status is strictly rejected."""
        payload = {
            'origin_warehouse': self.wh_source.id,
            'destination_address': 'Client Site D',
            'item': self.item_limited.id,
            'quantity': 2,
            'vehicle': self.vehicle_maintenance.id,
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[BR-04 Vehicle Lockout]")

        # Vehicle status remains MAINTENANCE
        self.vehicle_maintenance.refresh_from_db()
        self.assertEqual(self.vehicle_maintenance.status, Vehicle.STATUS_MAINTENANCE)
        self.assertEqual(Shipment.objects.count(), 0)

    def test_depot_item_mismatch_rejection(self):
        """[BR-02] Origin warehouse must match item's actual warehouse depot."""
        payload = {
            'origin_warehouse': self.wh_other.id,  # Mismatched depot!
            'destination_address': 'Client Site E',
            'item': self.item_limited.id,
            'quantity': 1,
            'status': Shipment.STATUS_DISPATCHED,
        }
        response = self.client.post(reverse('shipment_dispatch'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[BR-02 Depot Mismatch]")
        self.assertEqual(Shipment.objects.count(), 0)

    def test_duplicate_seat_booking_rejected(self):
        """Reject assigning an already booked seat on the same schedule."""
        bus = Vehicle.objects.create(
            registration_number="DL-01-BS-9999",
            vehicle_type=Vehicle.TYPE_BUS,
            capacity=10,
            status=Vehicle.STATUS_AVAILABLE
        )
        route = TransitRoute.objects.create(
            route_code="ROUTE-TEST",
            origin_stop="Stop A",
            destination_stop="Stop B",
            duration_minutes=60
        )
        now = timezone.now()
        schedule = TransitSchedule.objects.create(
            route=route,
            vehicle=bus,
            departure_time=now + timedelta(hours=2),
            arrival_time=now + timedelta(hours=3),
            fare=100.00
        )

        # Pre-book seat 5
        TicketBooking.objects.create(
            schedule=schedule,
            passenger_name="Existing Passenger",
            passenger_email="existing@example.com",
            seat_number=5,
            status=TicketBooking.STATUS_CONFIRMED
        )

        # Attempt to book seat 5 again
        response = self.client.post(
            reverse('book_ticket', kwargs={'schedule_id': schedule.id}),
            {
                'passenger_name': 'Second Passenger',
                'passenger_email': 'second@example.com',
                'seat_number': 5
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seat 5 is already booked")

        # Booking count remains 1
        self.assertEqual(schedule.bookings.count(), 1)

    def test_nonexistent_tracking_code_graceful_handling(self):
        """[US-05] Searching for an unmanifested tracking code returns 200 with not-found banner without 500 error."""
        response = self.client.get(reverse('track_shipment'), {'q': 'LC-TRK-99999999-NOTFOUND'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tracking Number Not Found")
        self.assertTrue(response.context['not_found'])

    def test_nonexistent_transit_schedule_returns_404(self):
        """Accessing a non-existent schedule ID returns clean HTTP 404."""
        response = self.client.get('/transit/book/888888/')
        self.assertEqual(response.status_code, 404)

    def test_synthetic_data_domain_privacy_audit(self):
        """[BR-08] Standing test verifying 100% of booked passenger emails use @example.com."""
        bus = Vehicle.objects.create(
            registration_number="DL-01-BS-7777",
            vehicle_type=Vehicle.TYPE_BUS,
            capacity=10,
            status=Vehicle.STATUS_AVAILABLE
        )
        route = TransitRoute.objects.create(
            route_code="ROUTE-AUDIT",
            origin_stop="Audit A",
            destination_stop="Audit B",
            duration_minutes=45
        )
        now = timezone.now()
        schedule = TransitSchedule.objects.create(
            route=route,
            vehicle=bus,
            departure_time=now + timedelta(hours=1),
            arrival_time=now + timedelta(hours=2)
        )

        # Create valid synthetic bookings
        for i in range(1, 4):
            TicketBooking.objects.create(
                schedule=schedule,
                passenger_name=f"Synthetic Passenger {i}",
                passenger_email=f"passenger_{i}@example.com",
                seat_number=i,
                status=TicketBooking.STATUS_CONFIRMED
            )

        # Audit query: Any email NOT ending in @example.com?
        non_compliant_count = TicketBooking.objects.exclude(passenger_email__endswith="@example.com").count()
        self.assertEqual(non_compliant_count, 0)
