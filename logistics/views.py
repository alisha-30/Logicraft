import json
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint
from .forms import ShipmentDispatchForm
from transit.models import TransitRoute, TransitSchedule, TicketBooking


def home_view(request):
    """
    [US-01, BR-01, TR-01] Executive Operations Performance Dashboard for the Operations Director.
    Aggregates multi-depot stock levels, fleet operational states, and outbound shipments in real time.
    """
    # 1. Summary Metric Counters (TR-01)
    total_warehouses = Warehouse.objects.count()
    total_inventory_skus = InventoryItem.objects.count()
    total_inventory_units = InventoryItem.objects.aggregate(total=Sum('quantity'))['total'] or 0

    vehicles_available = Vehicle.objects.filter(status=Vehicle.STATUS_AVAILABLE).count()
    vehicles_in_transit = Vehicle.objects.filter(status=Vehicle.STATUS_IN_TRANSIT).count()
    vehicles_maintenance = Vehicle.objects.filter(status=Vehicle.STATUS_MAINTENANCE).count()
    vehicles_total = Vehicle.objects.count()

    shipments_total = Shipment.objects.count()
    shipments_active = Shipment.objects.exclude(
        status__in=[Shipment.STATUS_DELIVERED, Shipment.STATUS_CANCELLED]
    ).count()
    shipments_delivered = Shipment.objects.filter(status=Shipment.STATUS_DELIVERED).count()

    transit_routes_count = TransitRoute.objects.count()
    transit_schedules_count = TransitSchedule.objects.count()
    transit_bookings_count = TicketBooking.objects.filter(status=TicketBooking.STATUS_CONFIRMED).count()

    stats = {
        'total_warehouses': total_warehouses,
        'total_inventory_skus': total_inventory_skus,
        'total_inventory_units': total_inventory_units,
        'vehicles_available': vehicles_available,
        'vehicles_in_transit': vehicles_in_transit,
        'vehicles_maintenance': vehicles_maintenance,
        'vehicles_total': vehicles_total,
        'shipments_total': shipments_total,
        'shipments_active': shipments_active,
        'shipments_delivered': shipments_delivered,
        'transit_routes': transit_routes_count,
        'transit_schedules': transit_schedules_count,
        'transit_bookings': transit_bookings_count,
    }

    # 2. Chart 1 Data: Stock Volume by Regional Warehouse Depot
    wh_stock_qs = Warehouse.objects.annotate(
        total_units=Sum('inventory_items__quantity')
    ).values('code', 'name', 'total_units', 'capacity_sqft')

    chart_wh_labels = [f"{w['code']}" for w in wh_stock_qs]
    chart_wh_units = [int(w['total_units'] or 0) for w in wh_stock_qs]

    # 3. Chart 2 Data: Fleet Operational Status Distribution (BR-04)
    chart_fleet_labels = ['Available', 'In Transit', 'Under Maintenance']
    chart_fleet_counts = [vehicles_available, vehicles_in_transit, vehicles_maintenance]

    # 4. Chart 3 Data: Shipment Pipeline by State (BR-01)
    status_counts = Shipment.objects.values('status').annotate(count=Count('id'))
    status_dict = {item['status']: item['count'] for item in status_counts}
    chart_shipment_labels = ['Pending', 'Dispatched', 'In Transit', 'Delivered', 'Cancelled']
    chart_shipment_counts = [
        status_dict.get(Shipment.STATUS_PENDING, 0),
        status_dict.get(Shipment.STATUS_DISPATCHED, 0),
        status_dict.get(Shipment.STATUS_IN_TRANSIT, 0),
        status_dict.get(Shipment.STATUS_DELIVERED, 0),
        status_dict.get(Shipment.STATUS_CANCELLED, 0),
    ]

    # 5. Actionable Alerts (Hitting Edge Cases from docs/09_data_design.md)
    low_stock_items = InventoryItem.objects.select_related('warehouse').filter(quantity__lte=3)[:5]
    maintenance_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_MAINTENANCE)[:5]

    # 6. Recent Activity Feed
    recent_shipments = Shipment.objects.select_related(
        'origin_warehouse', 'item', 'vehicle'
    ).order_by('-created_at')[:8]

    recent_checkpoints = ShipmentCheckpoint.objects.select_related(
        'shipment'
    ).order_by('-timestamp')[:5]

    return render(request, 'home.html', {
        'stats': stats,
        'chart_wh_labels': json.dumps(chart_wh_labels),
        'chart_wh_units': json.dumps(chart_wh_units),
        'chart_fleet_labels': json.dumps(chart_fleet_labels),
        'chart_fleet_counts': json.dumps(chart_fleet_counts),
        'chart_shipment_labels': json.dumps(chart_shipment_labels),
        'chart_shipment_counts': json.dumps(chart_shipment_counts),
        'low_stock_items': low_stock_items,
        'maintenance_vehicles': maintenance_vehicles,
        'recent_shipments': recent_shipments,
        'recent_checkpoints': recent_checkpoints,
    })


def track_shipment_view(request):
    """
    [US-03, US-05, TC-04] Public tracking page allowing parcel lookups by tracking number.
    """
    query = request.GET.get('q', '').strip()
    shipment = None
    not_found = False

    if query:
        try:
            shipment = Shipment.objects.select_related(
                'origin_warehouse', 'vehicle', 'item'
            ).prefetch_related('checkpoints').get(tracking_number__iexact=query)
        except Shipment.DoesNotExist:
            not_found = True

    return render(request, 'logistics/track_shipment.html', {
        'query': query,
        'shipment': shipment,
        'not_found': not_found,
    })


def inventory_catalog_view(request):
    """
    [US-02, BR-02, SCR-03] Warehouse Inventory Cataloging view.
    Allows warehouse supervisors and dispatchers to browse, filter by depot, and search SKUs.
    """
    warehouse_code = request.GET.get('warehouse', '').strip()
    category = request.GET.get('category', '').strip()
    query = request.GET.get('q', '').strip()

    items = InventoryItem.objects.select_related('warehouse').order_by('warehouse__code', 'name')

    if warehouse_code:
        items = items.filter(warehouse__code__iexact=warehouse_code)
    if category:
        items = items.filter(category__iexact=category)
    if query:
        items = items.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    warehouses = Warehouse.objects.all().order_by('code')
    categories = InventoryItem.objects.values_list('category', flat=True).distinct().order_by('category')

    total_skus = items.count()
    total_units = items.aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'logistics/inventory_catalog.html', {
        'items': items,
        'warehouses': warehouses,
        'categories': categories,
        'selected_warehouse': warehouse_code,
        'selected_category': category,
        'query': query,
        'total_skus': total_skus,
        'total_units': total_units,
    })


def login_view(request):
    """
    [TR-03, BR-08] Staff authentication with credential validation and error preservation.
    """
    if request.user.is_authenticated:
        return redirect('home')

    username_val = ""
    if request.method == 'POST':
        username_val = request.POST.get('username', '').strip()
        password_val = request.POST.get('password', '')

        if not username_val or not password_val:
            messages.error(request, "Both username and password are required.")
            return render(request, 'accounts/login.html', {'username': username_val})

        user = authenticate(request, username=username_val, password=password_val)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials.")
            return render(request, 'accounts/login.html', {'username': username_val})

    return render(request, 'accounts/login.html', {'username': username_val})


def register_view(request):
    """
    [TR-03, BR-08] Staff user registration with role domain assignment and privacy guardrails.
    """
    if request.user.is_authenticated:
        return redirect('home')

    context = {
        'username': '',
        'email': '',
        'role': 'DISPATCHER',
    }

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', 'DISPATCHER')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        context['username'] = username
        context['email'] = email
        context['role'] = role

        # Validation rules
        if not username or not email or not password:
            messages.error(request, "All required fields must be completed.")
            return render(request, 'accounts/register.html', context)

        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please re-enter matching passwords.")
            return render(request, 'accounts/register.html', context)

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters in length.")
            return render(request, 'accounts/register.html', context)

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already registered. Please choose another username.")
            return render(request, 'accounts/register.html', context)

        # Create user account
        user = User.objects.create_user(username=username, email=email, password=password)
        # Grant staff status for operations roles
        if role in ['DIRECTOR', 'SUPERVISOR', 'DISPATCHER']:
            user.is_staff = True
            user.save()

        login(request, user)
        messages.success(request, f"Account successfully created for {user.username}! You are now signed in.")
        return redirect('home')

    return render(request, 'accounts/register.html', context)


def logout_view(request):
    """
    Staff sign-out handler.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been securely signed out.")
    return redirect('home')


def shipment_dispatch_view(request):
    """
    [US-02, US-03, US-04, BR-02, BR-03, BR-04, TR-02, TR-03]
    Interactive form to create outbound shipments and dispatch freight.
    Transactionally decrements origin inventory and switches vehicle status to IN_TRANSIT.
    """
    if request.method == 'POST':
        form = ShipmentDispatchForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    shipment = form.save(commit=False)

                    # Deduct stock if dispatched immediately
                    if shipment.status in [Shipment.STATUS_DISPATCHED, Shipment.STATUS_IN_TRANSIT]:
                        item = InventoryItem.objects.select_for_update().get(id=shipment.item_id)
                        if item.quantity < shipment.quantity:
                            form.add_error(
                                'quantity',
                                f"[BR-03 Deficit] Insufficient stock. Current available: {item.quantity} {item.unit}."
                            )
                            raise ValidationError("Insufficient inventory on hand.")

                        item.quantity -= shipment.quantity
                        item.save(update_fields=['quantity', 'updated_at'])

                        # Lock vehicle into in-transit state
                        if shipment.vehicle:
                            veh = Vehicle.objects.select_for_update().get(id=shipment.vehicle_id)
                            veh.status = Vehicle.STATUS_IN_TRANSIT
                            veh.save(update_fields=['status', 'updated_at'])

                    shipment.save()

                    # Create initial audit waypoint checkpoint
                    ShipmentCheckpoint.objects.create(
                        shipment=shipment,
                        location_name=f"{shipment.origin_warehouse.name} ({shipment.origin_warehouse.code})",
                        status_note=f"Shipment manifested ({shipment.get_status_display()}). Assigned Vehicle: {shipment.vehicle.registration_number if shipment.vehicle else 'Awaiting assignment'}."
                    )

                    messages.success(
                        request,
                        f"Shipment {shipment.tracking_number} successfully manifested! "
                        f"{shipment.quantity} {shipment.item.unit} deducted from {shipment.origin_warehouse.code} inventory."
                    )
                    return redirect(f"/track/?q={shipment.tracking_number}")
            except ValidationError:
                pass

        messages.error(request, "Failed to manifest shipment. Please review the errors highlighted below.")
    else:
        form = ShipmentDispatchForm()

    # Context data for dynamic client-side interactivity
    items_qs = InventoryItem.objects.select_related('warehouse').all()
    items_meta = {
        item.id: {
            'sku': item.sku,
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.unit,
            'warehouse_id': item.warehouse_id,
            'warehouse_code': item.warehouse.code,
            'warehouse_name': item.warehouse.name,
        }
        for item in items_qs
    }

    vehicles_qs = Vehicle.objects.all()
    vehicles_meta = {
        veh.id: {
            'reg': veh.registration_number,
            'type': veh.get_vehicle_type_display(),
            'capacity': veh.capacity,
            'status': veh.status,
            'is_maintenance': (veh.status == Vehicle.STATUS_MAINTENANCE),
        }
        for veh in vehicles_qs
    }

    recent_dispatches = Shipment.objects.select_related(
        'origin_warehouse', 'item', 'vehicle'
    ).order_by('-created_at')[:8]

    return render(request, 'logistics/dispatch_form.html', {
        'form': form,
        'items_json': json.dumps(items_meta),
        'vehicles_json': json.dumps(vehicles_meta),
        'recent_dispatches': recent_dispatches,
    })
