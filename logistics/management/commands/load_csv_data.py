import os
import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from logistics.models import Warehouse, InventoryItem, Vehicle, Shipment, ShipmentCheckpoint
from transit.models import TransitRoute, TransitSchedule, TicketBooking


class Command(BaseCommand):
    help = "Loads the synthetic CSV datasets from data/ into the active SQLite database."

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        data_dir = base_dir / "data"

        if not data_dir.exists():
            self.stderr.write(self.style.ERROR(f"Data directory not found at {data_dir}. Run 'python src/generate_data.py' first."))
            return

        self.stdout.write(self.style.NOTICE("Ingesting synthetic CSV datasets into SQLite database..."))

        try:
            with transaction.atomic():
                # 1. Clear existing application data (reverse dependency order)
                TicketBooking.objects.all().delete()
                TransitSchedule.objects.all().delete()
                TransitRoute.objects.all().delete()
                ShipmentCheckpoint.objects.all().delete()
                Shipment.objects.all().delete()
                InventoryItem.objects.all().delete()
                Vehicle.objects.all().delete()
                Warehouse.objects.all().delete()

                # 2. Warehouses
                df_wh = pd.read_csv(data_dir / "warehouses.csv")
                warehouses = [
                    Warehouse(
                        id=row["id"],
                        code=row["code"],
                        name=row["name"],
                        address=row["address"],
                        capacity_sqft=row["capacity_sqft"],
                        created_at=row["created_at"]
                    )
                    for _, row in df_wh.iterrows()
                ]
                Warehouse.objects.bulk_create(warehouses)
                self.stdout.write(f"  [OK] Ingested {len(warehouses)} Warehouses")

                # 3. Inventory Items
                df_items = pd.read_csv(data_dir / "inventory_items.csv")
                items = [
                    InventoryItem(
                        id=row["id"],
                        warehouse_id=row["warehouse_id"],
                        sku=row["sku"],
                        name=row["name"],
                        category=row["category"],
                        quantity=row["quantity"],
                        unit=row["unit"],
                        updated_at=row["updated_at"]
                    )
                    for _, row in df_items.iterrows()
                ]
                InventoryItem.objects.bulk_create(items)
                self.stdout.write(f"  [OK] Ingested {len(items)} Inventory Items")

                # 4. Vehicles
                df_v = pd.read_csv(data_dir / "vehicles.csv")
                vehicles = [
                    Vehicle(
                        id=row["id"],
                        registration_number=row["registration_number"],
                        vehicle_type=row["vehicle_type"],
                        capacity=row["capacity"],
                        status=row["status"],
                        notes=row["notes"] if pd.notna(row["notes"]) else "",
                        updated_at=row["updated_at"]
                    )
                    for _, row in df_v.iterrows()
                ]
                Vehicle.objects.bulk_create(vehicles)
                self.stdout.write(f"  [OK] Ingested {len(vehicles)} Vehicles")

                # 5. Shipments
                df_ship = pd.read_csv(data_dir / "shipments.csv")
                shipments = []
                for _, row in df_ship.iterrows():
                    v_id = int(row["vehicle_id"]) if pd.notna(row["vehicle_id"]) else None
                    est_deliv = row["estimated_delivery_date"] if pd.notna(row["estimated_delivery_date"]) else None
                    d_name = row["driver_name"] if pd.notna(row["driver_name"]) else ""
                    shipments.append(Shipment(
                        id=row["id"],
                        tracking_number=row["tracking_number"],
                        origin_warehouse_id=row["origin_warehouse_id"],
                        item_id=row["item_id"],
                        vehicle_id=v_id,
                        driver_name=d_name,
                        destination_address=row["destination_address"],
                        quantity=row["quantity"],
                        status=row["status"],
                        estimated_delivery_date=est_deliv,
                        created_at=row["created_at"],
                        updated_at=row["updated_at"]
                    ))
                Shipment.objects.bulk_create(shipments)
                self.stdout.write(f"  [OK] Ingested {len(shipments)} Shipments")

                # 6. Checkpoints
                df_cp = pd.read_csv(data_dir / "shipment_checkpoints.csv")
                checkpoints = [
                    ShipmentCheckpoint(
                        id=row["id"],
                        shipment_id=row["shipment_id"],
                        location_name=row["location_name"],
                        status_note=row["status_note"],
                        timestamp=row["timestamp"]
                    )
                    for _, row in df_cp.iterrows()
                ]
                ShipmentCheckpoint.objects.bulk_create(checkpoints)
                self.stdout.write(f"  [OK] Ingested {len(checkpoints)} Shipment Checkpoints")

                # 7. Transit Routes
                df_routes = pd.read_csv(data_dir / "transit_routes.csv")
                routes = [
                    TransitRoute(
                        id=row["id"],
                        route_code=row["route_code"],
                        origin_stop=row["origin_stop"],
                        destination_stop=row["destination_stop"],
                        duration_minutes=row["duration_minutes"]
                    )
                    for _, row in df_routes.iterrows()
                ]
                TransitRoute.objects.bulk_create(routes)
                self.stdout.write(f"  [OK] Ingested {len(routes)} Transit Routes")

                # 8. Transit Schedules
                df_sched = pd.read_csv(data_dir / "transit_schedules.csv")
                schedules = [
                    TransitSchedule(
                        id=row["id"],
                        route_id=row["route_id"],
                        vehicle_id=row["vehicle_id"],
                        departure_time=row["departure_time"],
                        arrival_time=row["arrival_time"],
                        fare=row["fare"]
                    )
                    for _, row in df_sched.iterrows()
                ]
                TransitSchedule.objects.bulk_create(schedules)
                self.stdout.write(f"  [OK] Ingested {len(schedules)} Transit Schedules")

                # 9. Ticket Bookings
                df_bk = pd.read_csv(data_dir / "ticket_bookings.csv")
                bookings = [
                    TicketBooking(
                        id=row["id"],
                        booking_reference=row["booking_reference"],
                        schedule_id=row["schedule_id"],
                        passenger_name=row["passenger_name"],
                        passenger_email=row["passenger_email"],
                        seat_number=row["seat_number"],
                        status=row["status"],
                        created_at=row["created_at"]
                    )
                    for _, row in df_bk.iterrows()
                ]
                TicketBooking.objects.bulk_create(bookings)
                self.stdout.write(f"  [OK] Ingested {len(bookings)} Ticket Bookings")

            self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Entire synthetic dataset imported successfully into SQLite!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to load CSV datasets: {e}"))
            raise e
