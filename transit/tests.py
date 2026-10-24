from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from logistics.models import Vehicle
from .models import TransitRoute, TransitSchedule, TicketBooking


class TransitModelTests(TestCase):
    def setUp(self):
        self.bus = Vehicle.objects.create(
            registration_number="BUS-CAP-2",
            vehicle_type=Vehicle.TYPE_BUS,
            capacity=2,  # Tiny capacity for testing capacity limits
            status=Vehicle.STATUS_AVAILABLE
        )
        self.route = TransitRoute.objects.create(
            route_code="TEST-ROUTE-1",
            origin_stop="Stop A",
            destination_stop="Stop B",
            duration_minutes=30
        )
        now = timezone.now()
        self.schedule = TransitSchedule.objects.create(
            route=self.route,
            vehicle=self.bus,
            departure_time=now + timedelta(hours=2),
            arrival_time=now + timedelta(hours=2, minutes=30),
            fare=50.00
        )

    def test_tc01_prevent_overbooking_when_capacity_full(self):
        """[TC-01, BR-04] Ensure booking is rejected when remaining seats = 0."""
        # Book seat 1
        TicketBooking.objects.create(
            schedule=self.schedule,
            passenger_name="User One",
            passenger_email="u1@test.com",
            seat_number=1,
            status=TicketBooking.STATUS_CONFIRMED
        )
        # Book seat 2 (now capacity is full: 2/2)
        TicketBooking.objects.create(
            schedule=self.schedule,
            passenger_name="User Two",
            passenger_email="u2@test.com",
            seat_number=2,
            status=TicketBooking.STATUS_CONFIRMED
        )

        self.assertEqual(self.schedule.remaining_seats(), 0)

        # Attempt to book a 3rd seat (should trigger ValidationError)
        booking_over = TicketBooking(
            schedule=self.schedule,
            passenger_name="User Three",
            passenger_email="u3@test.com",
            seat_number=3,
            status=TicketBooking.STATUS_CONFIRMED
        )
        with self.assertRaises(ValidationError):
            booking_over.full_clean()

    def test_booking_web_view_when_full(self):
        """[TC-01] Ensure web view redirects with error when user posts to fully booked route."""
        # Fill capacity
        TicketBooking.objects.create(
            schedule=self.schedule,
            passenger_name="User One",
            passenger_email="u1@test.com",
            seat_number=1,
            status=TicketBooking.STATUS_CONFIRMED
        )
        TicketBooking.objects.create(
            schedule=self.schedule,
            passenger_name="User Two",
            passenger_email="u2@test.com",
            seat_number=2,
            status=TicketBooking.STATUS_CONFIRMED
        )

        client = Client()
        response = client.post(reverse('book_ticket', args=[self.schedule.id]), {
            'passenger_name': 'Late User',
            'passenger_email': 'late@test.com',
            'seat_number': 1
        }, follow=True)

        self.assertContains(response, "currently sold out")
