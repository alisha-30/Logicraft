from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class TransitRoute(models.Model):
    """
    [TR-02, US-06] Fixed transit corridor between two passenger stops.
    """
    route_code = models.CharField(max_length=20, unique=True, help_text="e.g. ROUTE-101")
    origin_stop = models.CharField(max_length=100, help_text="e.g. Central Bus Terminal")
    destination_stop = models.CharField(max_length=100, help_text="e.g. Airport Terminal 3")
    duration_minutes = models.PositiveIntegerField(help_text="Estimated trip duration in minutes")

    def __str__(self):
        return f"{self.route_code}: {self.origin_stop} -> {self.destination_stop}"


class TransitSchedule(models.Model):
    """
    [TR-02, US-06, BR-04] Scheduled departure for a route assigned to a transit vehicle.
    """
    route = models.ForeignKey(TransitRoute, on_delete=models.CASCADE, related_name='schedules')
    vehicle = models.ForeignKey(
        'logistics.Vehicle',
        on_delete=models.PROTECT,
        related_name='transit_trips',
        limit_choices_to={'vehicle_type': 'BUS'},
        help_text="Assigned passenger bus"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    fare = models.DecimalField(max_digits=7, decimal_places=2, default=50.00, help_text="Ticket price in INR")

    def remaining_seats(self):
        """
        [BR-04, TC-01] Deterministic seat remaining calculation:
        Remaining = Vehicle Capacity - Confirmed Bookings
        """
        total_capacity = self.vehicle.capacity
        confirmed_bookings = self.bookings.filter(status=TicketBooking.STATUS_CONFIRMED).count()
        return max(0, total_capacity - confirmed_bookings)

    def clean(self):
        super().clean()
        if self.arrival_time and self.departure_time and self.arrival_time <= self.departure_time:
            raise ValidationError({"arrival_time": "Arrival time must be strictly after departure time."})

    def __str__(self):
        dept_str = self.departure_time.strftime('%d-%b %H:%M')
        return f"{self.route.route_code} at {dept_str} (Bus: {self.vehicle.registration_number})"


def generate_booking_reference():
    """
    Generates unique ticket booking reference: LC-TKT-XXXXXX
    """
    return f"LC-TKT-{uuid.uuid4().hex[:8].upper()}"


class TicketBooking(models.Model):
    """
    [TR-02, US-05, BR-04, TC-01] Passenger seat reservations.
    """
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    booking_reference = models.CharField(
        max_length=32,
        unique=True,
        default=generate_booking_reference,
        editable=False
    )
    schedule = models.ForeignKey(TransitSchedule, on_delete=models.CASCADE, related_name='bookings')
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    seat_number = models.PositiveIntegerField(help_text="Seat number assigned")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        # [BR-04, TC-01] Capacity validation on booking creation
        if self.pk is None and self.status == self.STATUS_CONFIRMED:
            if self.schedule.remaining_seats() <= 0:
                raise ValidationError(f"Cannot book ticket: Schedule {self.schedule} is fully booked (0 remaining seats).")

        # Seat boundary check
        if self.schedule and self.seat_number > self.schedule.vehicle.capacity:
            raise ValidationError({"seat_number": f"Seat number cannot exceed vehicle capacity ({self.schedule.vehicle.capacity})."})

    def __str__(self):
        return f"{self.booking_reference} - {self.passenger_name} (Seat {self.seat_number})"
