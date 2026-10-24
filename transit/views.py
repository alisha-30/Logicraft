from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import TransitRoute, TransitSchedule, TicketBooking


def transit_schedules_view(request):
    """
    [US-05] Public view to search bus routes and timetables.
    """
    origin = request.GET.get('origin', '').strip()
    destination = request.GET.get('destination', '').strip()

    schedules = TransitSchedule.objects.select_related('route', 'vehicle').order_by('departure_time')

    if origin:
        schedules = schedules.filter(route__origin_stop__icontains=origin)
    if destination:
        schedules = schedules.filter(route__destination_stop__icontains=destination)

    # Attach computed remaining seats to each schedule object for display
    schedule_data = []
    for sched in schedules:
        schedule_data.append({
            'schedule': sched,
            'seats_left': sched.remaining_seats(),
        })

    return render(request, 'transit/schedule_list.html', {
        'schedules': schedule_data,
        'origin_query': origin,
        'dest_query': destination,
    })


def book_ticket_view(request, schedule_id):
    """
    [US-05, BR-04, TC-01] Books a ticket on an available transit schedule.
    """
    schedule = get_object_or_404(TransitSchedule.objects.select_related('route', 'vehicle'), pk=schedule_id)
    seats_left = schedule.remaining_seats()

    if request.method == 'POST':
        # [BR-04, TC-01] Reject if capacity full
        if seats_left <= 0:
            messages.error(request, f"Cannot book: Route {schedule.route.route_code} is currently sold out (0 seats remaining).")
            return redirect('transit_schedules')

        name = request.POST.get('passenger_name', '').strip()
        email = request.POST.get('passenger_email', '').strip()
        seat_num = request.POST.get('seat_number', '').strip()

        if not name or not email or not seat_num:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'transit/book_ticket.html', {'schedule': schedule, 'seats_left': seats_left})

        try:
            seat_num = int(seat_num)
            if seat_num < 1 or seat_num > schedule.vehicle.capacity:
                messages.error(request, f"Seat number must be between 1 and {schedule.vehicle.capacity}.")
                return render(request, 'transit/book_ticket.html', {'schedule': schedule, 'seats_left': seats_left})

            # Check if this seat number is already booked for this schedule
            if TicketBooking.objects.filter(schedule=schedule, seat_number=seat_num, status=TicketBooking.STATUS_CONFIRMED).exists():
                messages.error(request, f"Seat {seat_num} is already booked. Please choose another seat.")
                return render(request, 'transit/book_ticket.html', {'schedule': schedule, 'seats_left': seats_left})

            booking = TicketBooking.objects.create(
                schedule=schedule,
                passenger_name=name,
                passenger_email=email,
                seat_number=seat_num,
                status=TicketBooking.STATUS_CONFIRMED
            )

            messages.success(request, f"Seat reserved successfully! Booking Ref: {booking.booking_reference}")
            return render(request, 'transit/booking_confirmation.html', {'booking': booking})

        except ValueError:
            messages.error(request, "Invalid seat number.")

    return render(request, 'transit/book_ticket.html', {
        'schedule': schedule,
        'seats_left': seats_left,
    })
