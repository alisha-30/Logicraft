from django.contrib import admin
from .models import TransitRoute, TransitSchedule, TicketBooking


@admin.register(TransitRoute)
class TransitRouteAdmin(admin.ModelAdmin):
    list_display = ('route_code', 'origin_stop', 'destination_stop', 'duration_minutes')
    search_fields = ('route_code', 'origin_stop', 'destination_stop')


class TicketBookingInline(admin.TabularInline):
    model = TicketBooking
    extra = 0
    readonly_fields = ('booking_reference', 'created_at')


@admin.register(TransitSchedule)
class TransitScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'vehicle', 'departure_time', 'arrival_time', 'fare', 'seats_left')
    list_filter = ('route', 'departure_time')
    inlines = [TicketBookingInline]

    def seats_left(self, obj):
        return obj.remaining_seats()
    seats_left.short_description = "Remaining Seats"


@admin.register(TicketBooking)
class TicketBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'passenger_name', 'schedule', 'seat_number', 'status', 'created_at')
    list_filter = ('status', 'schedule__route')
    search_fields = ('booking_reference', 'passenger_name', 'passenger_email')
