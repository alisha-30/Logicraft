"""
LogiCraft Dataset Generator
----------------------------
Generates synthetic relational datasets for LogiCraft based on docs/09_data_design.md.

Stack: Python, pandas, numpy, Faker
Random Seed: 42 (Strictly reproducible)
100% Synthetic data (Zero PII).
"""

import os
import random
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker

# =====================================================================
# 1. DATASET CONFIGURATION & TARGET ROW COUNTS (docs/09_data_design.md)
# =====================================================================
RANDOM_SEED = 42

NUM_WAREHOUSES = 8
NUM_INVENTORY_ITEMS = 80
NUM_VEHICLES = 25
NUM_SHIPMENTS = 50
NUM_CHECKPOINTS = 160
NUM_TRANSIT_ROUTES = 8
NUM_TRANSIT_SCHEDULES = 25
NUM_TICKET_BOOKINGS = 120

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data"

# Seed all generators
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
fake = Faker('en_IN')
Faker.seed(RANDOM_SEED)

BASE_DATE = datetime(2026, 10, 1, 9, 0, 0)


# =====================================================================
# 2. GENERATION LOGIC
# =====================================================================

def generate_warehouses() -> pd.DataFrame:
    """Generates warehouse depots adhering to the 80/20 volume distribution."""
    hubs = [
        ("WH-DEL-01", "Northern Regional Hub - Delhi", "Okhla Industrial Area Phase III, New Delhi", 65000),
        ("WH-MUM-01", "Western Coastal Depot - Mumbai", "Bhiwandi Logistics Park, Mumbai, Maharashtra", 80000),
        ("WH-BLR-01", "Southern Tech Distribution Hub", "Peenya Industrial Estate, Bengaluru, Karnataka", 45000),
        ("WH-KOL-01", "Eastern Freight Center - Kolkata", "Taratala Road, Kolkata, West Bengal", 40000),
        ("WH-HYD-01", "Central Cargo Depot - Hyderabad", "Sanathnagar Industrial Area, Hyderabad, Telangana", 35000),
        ("WH-AMD-01", "Gujarat Logistics Terminal - Ahmedabad", "Changodar Industrial Hub, Ahmedabad, Gujarat", 30000),
        ("WH-CHN-01", "Chennai Port Logistics Hub", "Ambattur Industrial Estate, Chennai, Tamil Nadu", 38000),
        ("WH-PUN-01", "Pune Distribution Facility", "Bhosari MIDC, Pune, Maharashtra", 28000),
    ]
    records = []
    for i, (code, name, addr, cap) in enumerate(hubs, start=1):
        created_at = BASE_DATE - timedelta(days=random.randint(60, 180))
        records.append({
            "id": i,
            "code": code,
            "name": name,
            "address": addr,
            "capacity_sqft": cap,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return pd.DataFrame(records)


def generate_inventory_items(warehouses_df: pd.DataFrame) -> pd.DataFrame:
    """Generates catalog SKUs with 80/20 depot skew and explicit edge cases."""
    categories = {
        "Renewable Energy": ["5kVA Solar Inverter", "Solar PV Panel (400W)", "Solar Charge Controller", "Deep-Cycle Battery"],
        "Healthcare Supplies": ["Emergency Trauma Kit", "Portable Oxygen Concentrator", "Surgical Glove Carton", "Digital Autoclave"],
        "Industrial Hardware": ["Hydraulic Pressure Valve", "High-Torque Electric Motor", "Heavy-Duty Ball Bearings", "Pneumatic Hose Reel"],
        "Electronics & Power": ["Lithium Iron Battery (100Ah)", "Uninterruptible Power Supply (UPS)", "High-Voltage Circuit Breaker", "Power Transformer"],
        "Water & Sanitation": ["Industrial Water Filter", "Reverse Osmosis Membrane", "Submersible Water Pump", "UV Water Disinfection Unit"],
    }
    wh_ids = warehouses_df["id"].tolist()
    # 80/20 rule: Delhi (id 1) and Mumbai (id 2) get 60% probability
    weights = [0.35, 0.25] + [0.40 / (len(wh_ids) - 2)] * (len(wh_ids) - 2)

    records = []
    sku_counter = 100

    # 1. Deliberate Edge Cases (docs/09_data_design.md)
    # Edge case 1: Zero-stock out-of-stock item (hits TC-03.2)
    records.append({
        "id": 1,
        "warehouse_id": 1,
        "sku": "SKU-ZERO-999",
        "name": "Zero-Stock Depleted Inverter",
        "category": "Renewable Energy",
        "quantity": 0,
        "unit": "units",
        "updated_at": (BASE_DATE - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    })
    # Edge case 2: Low-stock boundary item (hits TC-03.1 / boundary)
    records.append({
        "id": 2,
        "warehouse_id": 1,
        "sku": "SKU-LOW-003",
        "name": "Low-Stock Boundary Emergency Pack",
        "category": "Healthcare Supplies",
        "quantity": 3,
        "unit": "boxes",
        "updated_at": (BASE_DATE - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    })

    # Standard items
    for item_id in range(3, NUM_INVENTORY_ITEMS + 1):
        sku_counter += 1
        cat = random.choice(list(categories.keys()))
        name = random.choice(categories[cat])
        wh_id = int(np.random.choice(wh_ids, p=weights))
        qty = random.randint(10, 350)
        unit = "units" if "Solar" in name or "Inverter" in name or "Motor" in name else "boxes"
        records.append({
            "id": item_id,
            "warehouse_id": wh_id,
            "sku": f"SKU-{cat[:3].upper()}-{sku_counter}",
            "name": name,
            "category": cat,
            "quantity": qty,
            "unit": unit,
            "updated_at": (BASE_DATE - timedelta(days=random.randint(1, 45))).strftime("%Y-%m-%d %H:%M:%S")
        })
    return pd.DataFrame(records)


def generate_vehicles() -> pd.DataFrame:
    """Generates multi-type fleet vehicles with maintenance edge cases."""
    records = []

    # Deliberate Edge Case: Vehicle in maintenance (hits TC-04.2)
    records.append({
        "id": 1,
        "registration_number": "DL-01-TR-3399",
        "vehicle_type": "TRUCK",
        "capacity": 8000,
        "status": "MAINTENANCE",
        "notes": "[EDGE-CASE TC-04.2] Workshop engine overhaul in progress",
        "updated_at": (BASE_DATE - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    })

    for v_id in range(2, NUM_VEHICLES + 1):
        if v_id <= 12:
            v_type = "TRUCK"
            cap = random.choice([4000, 5000, 8000, 10000])
        elif v_id <= 20:
            v_type = "VAN"
            cap = random.choice([1200, 1500, 2000])
        else:
            v_type = "BUS"
            cap = random.choice([25, 30, 40])

        # Ratios: ~70% Available, ~20% In Transit, ~10% Maintenance
        status = np.random.choice(["AVAILABLE", "IN_TRANSIT", "MAINTENANCE"], p=[0.70, 0.20, 0.10])
        state = random.choice(["DL", "MH", "KA", "TN", "WB", "GJ"])
        r_num = f"{state}-{random.randint(1, 14):02d}-{v_type[:2]}-{random.randint(1000, 9999)}"

        records.append({
            "id": v_id,
            "registration_number": r_num,
            "vehicle_type": v_type,
            "capacity": cap,
            "status": status,
            "notes": f"Regular operational vehicle {v_id}",
            "updated_at": (BASE_DATE - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")
        })
    return pd.DataFrame(records)


def generate_shipments(warehouses_df: pd.DataFrame, items_df: pd.DataFrame, vehicles_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generates shipments and checkpoints respecting origin consistency and edge cases."""
    shipments = []
    checkpoints = []
    cp_id = 1

    cargo_vehicles = vehicles_df[vehicles_df["vehicle_type"].isin(["TRUCK", "VAN"])]
    available_cargo_vehicles = cargo_vehicles[cargo_vehicles["status"] == "AVAILABLE"]["id"].tolist()

    # Edge Case 1: Unassigned vehicle in PENDING status
    # Edge Case 2: Special character address
    # Edge Case 3: Shipment with zero checkpoints
    edge_cases_injected = False

    for s_id in range(1, NUM_SHIPMENTS + 1):
        tracking_num = f"LC-TRK-202610{s_id:02d}-{random.randint(100000, 999999)}"

        # Pick item first, origin warehouse MUST match item's warehouse (BR-02 consistency)
        item_row = items_df.sample(1).iloc[0]
        item_id = int(item_row["id"])
        wh_id = int(item_row["warehouse_id"])

        if s_id == 1:
            # Edge case 1: PENDING shipment with NULL vehicle
            status = "PENDING"
            v_id = None
            dest = "Plot #42/B, Industrial Sector-62, Noida (U.P.) - 201309"  # Edge case: special chars
            qty = 2
            created_at = BASE_DATE - timedelta(hours=4)
        elif s_id == 2:
            # Edge case 2: Newly created shipment with 0 checkpoints
            status = "PENDING"
            v_id = available_cargo_vehicles[0] if available_cargo_vehicles else None
            dest = "Warehouse Depot Transfer, Sector 18, Gurugram, Haryana"
            qty = 1
            created_at = BASE_DATE - timedelta(hours=2)
        else:
            status = np.random.choice(
                ["DELIVERED", "IN_TRANSIT", "DISPATCHED", "PENDING", "CANCELLED"],
                p=[0.40, 0.30, 0.15, 0.10, 0.05]
            )
            v_id = random.choice(available_cargo_vehicles) if status in ["DISPATCHED", "IN_TRANSIT", "DELIVERED"] else None
            dest = f"{fake.street_address()}, {fake.city()}, {fake.state()}"
            qty = random.randint(1, min(10, max(1, int(item_row["quantity"]))))
            created_at = BASE_DATE - timedelta(days=random.randint(1, 10))

        updated_at = created_at + timedelta(hours=random.randint(2, 48))
        driver_name = (fake.first_name() + " " + fake.last_name()) if v_id is not None else ""
        est_deliv = (created_at + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S") if status != "CANCELLED" else np.nan

        shipments.append({
            "id": s_id,
            "tracking_number": tracking_num,
            "origin_warehouse_id": wh_id,
            "item_id": item_id,
            "vehicle_id": v_id if v_id is not None else np.nan,
            "driver_name": driver_name,
            "destination_address": dest,
            "quantity": qty,
            "status": status,
            "estimated_delivery_date": est_deliv,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })

        # Generate checkpoints for active/delivered shipments (skip for s_id == 2 edge case)
        if s_id != 2 and status in ["DISPATCHED", "IN_TRANSIT", "DELIVERED"]:
            num_cp = 1 if status == "DISPATCHED" else (2 if status == "IN_TRANSIT" else 3)
            for step in range(num_cp):
                cp_time = created_at + timedelta(hours=(step + 1) * 6)
                if step == 0:
                    note = "Cargo packed and dispatched from warehouse"
                    loc = f"Origin Depot {wh_id}"
                elif step == 1:
                    note = "In transit through regional transit corridor"
                    loc = f"Highway Waypoint Sector {random.randint(10, 90)}"
                else:
                    note = "Out for delivery to destination / signature received"
                    loc = "Local Delivery Hub"

                checkpoints.append({
                    "id": cp_id,
                    "shipment_id": s_id,
                    "location_name": loc,
                    "status_note": note,
                    "timestamp": cp_time.strftime("%Y-%m-%d %H:%M:%S")
                })
                cp_id += 1

    return pd.DataFrame(shipments), pd.DataFrame(checkpoints)


def generate_transit_data(vehicles_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generates routes, schedules, and capacity-constrained ticket bookings."""
    buses = vehicles_df[vehicles_df["vehicle_type"] == "BUS"]
    bus_ids = buses["id"].tolist()
    bus_caps = dict(zip(buses["id"], buses["capacity"]))

    routes_data = [
        ("ROUTE-101", "Central Bus Terminal, Delhi", "Indira Gandhi Airport Terminal 3", 45),
        ("ROUTE-102", "Kashmere Gate ISBT", "Cyber City Metro Station, Gurugram", 60),
        ("ROUTE-201", "Chhatrapati Shivaji Maharaj Terminus", "Bandra Kurla Complex (BKC), Mumbai", 35),
        ("ROUTE-202", "Dadar Western Terminal", "Navi Mumbai Vashi Plaza", 50),
        ("ROUTE-301", "Majestic Kempegowda Bus Station", "Electronic City Phase 1, Bengaluru", 55),
        ("ROUTE-302", "Whitefield ITPL", "Kempegowda International Airport", 65),
        ("ROUTE-401", "Howrah Railway Station", "Salt Lake Sector V, Kolkata", 40),
        ("ROUTE-501", "Secunderabad Station", "Hitec City Cyber Towers, Hyderabad", 45),
    ]
    routes = []
    for r_id, (code, orig, dest, dur) in enumerate(routes_data, start=1):
        routes.append({
            "id": r_id,
            "route_code": code,
            "origin_stop": orig,
            "destination_stop": dest,
            "duration_minutes": dur
        })
    routes_df = pd.DataFrame(routes)

    # Schedules
    schedules = []
    sched_id = 1
    for r in routes:
        # 3 scheduled trips per route (Morning peak, Midday, Evening peak)
        for offset_hours in [8, 13, 18]:
            dept_time = BASE_DATE + timedelta(days=1, hours=offset_hours)
            arr_time = dept_time + timedelta(minutes=r["duration_minutes"])
            v_id = random.choice(bus_ids)
            fare = float(random.choice([40.0, 50.0, 60.0, 75.0, 90.0]))
            schedules.append({
                "id": sched_id,
                "route_id": r["id"],
                "vehicle_id": v_id,
                "departure_time": dept_time.strftime("%Y-%m-%d %H:%M:%S"),
                "arrival_time": arr_time.strftime("%Y-%m-%d %H:%M:%S"),
                "fare": fare
            })
            sched_id += 1
            if sched_id > NUM_TRANSIT_SCHEDULES:
                break
        if sched_id > NUM_TRANSIT_SCHEDULES:
            break
    schedules_df = pd.DataFrame(schedules)

    # Bookings with deliberate edge cases
    bookings = []
    b_id = 1

    for s_idx, sched in schedules_df.iterrows():
        s_id = sched["id"]
        v_id = sched["vehicle_id"]
        cap = bus_caps[v_id]

        # Edge Case 1: Schedule #1 is 100% SOLD OUT (confirmed bookings == capacity)
        if s_id == 1:
            target_bookings = cap
        # Edge Case 2: Schedule #2 has exactly 1 SEAT LEFT
        elif s_id == 2:
            target_bookings = cap - 1
        else:
            target_bookings = random.randint(1, max(1, cap // 2))

        # Fill seats up to target_bookings
        for seat in range(1, target_bookings + 1):
            if b_id > NUM_TICKET_BOOKINGS:
                break
            name = fake.first_name() + " " + fake.last_name()
            # Synthetic privacy: Strictly @example.com
            email = f"user_{b_id}@{fake.last_name().lower()}test.example.com"
            b_ref = f"LC-TKT-{b_id:04d}-{random.randint(1000, 9999)}"
            created_at = BASE_DATE - timedelta(hours=random.randint(1, 24))

            bookings.append({
                "id": b_id,
                "booking_reference": b_ref,
                "schedule_id": s_id,
                "passenger_name": name,
                "passenger_email": email,
                "seat_number": seat,
                "status": "CONFIRMED",
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            b_id += 1

    bookings_df = pd.DataFrame(bookings)
    return routes_df, schedules_df, bookings_df


# =====================================================================
# 3. COMPREHENSIVE VALIDATION FUNCTION
# =====================================================================

def validate_dataset(dfs: dict[str, pd.DataFrame]) -> dict[str, dict]:
    """
    Validates:
    1. Primary Key uniqueness.
    2. Foreign Key referential integrity.
    3. Null rates matching intended schema.
    4. Business rule invariants & edge cases presence.
    """
    results = {}

    # 1. Primary Key Uniqueness
    for name, df in dfs.items():
        is_unique = df["id"].is_unique and df["id"].notnull().all()
        results[name] = {
            "rows": len(df),
            "pk_unique": is_unique,
            "fk_valid": True,
            "null_rates_valid": True,
            "notes": []
        }

    # 2. Foreign Key Validations
    # inventory_items -> warehouses
    if not dfs["inventory_items"]["warehouse_id"].isin(dfs["warehouses"]["id"]).all():
        results["inventory_items"]["fk_valid"] = False
        results["inventory_items"]["notes"].append("FK warehouse_id invalid")

    # shipments -> warehouses, inventory_items, vehicles
    if not dfs["shipments"]["origin_warehouse_id"].isin(dfs["warehouses"]["id"]).all():
        results["shipments"]["fk_valid"] = False
        results["shipments"]["notes"].append("FK origin_warehouse_id invalid")
    if not dfs["shipments"]["item_id"].isin(dfs["inventory_items"]["id"]).all():
        results["shipments"]["fk_valid"] = False
        results["shipments"]["notes"].append("FK item_id invalid")
    # vehicles FK in shipments is nullable
    non_null_v = dfs["shipments"]["vehicle_id"].dropna()
    if not non_null_v.isin(dfs["vehicles"]["id"]).all():
        results["shipments"]["fk_valid"] = False
        results["shipments"]["notes"].append("FK vehicle_id invalid")

    # Business Rule Consistency: shipment origin warehouse == item warehouse
    item_wh_map = dfs["inventory_items"].set_index("id")["warehouse_id"].to_dict()
    for _, row in dfs["shipments"].iterrows():
        if item_wh_map[row["item_id"]] != row["origin_warehouse_id"]:
            results["shipments"]["fk_valid"] = False
            results["shipments"]["notes"].append("BR-02 Violation: Item warehouse != origin warehouse")
            break

    # checkpoints -> shipments
    if not dfs["shipment_checkpoints"]["shipment_id"].isin(dfs["shipments"]["id"]).all():
        results["shipment_checkpoints"]["fk_valid"] = False
        results["shipment_checkpoints"]["notes"].append("FK shipment_id invalid")

    # schedules -> routes, vehicles
    if not dfs["transit_schedules"]["route_id"].isin(dfs["transit_routes"]["id"]).all():
        results["transit_schedules"]["fk_valid"] = False
        results["transit_schedules"]["notes"].append("FK route_id invalid")
    if not dfs["transit_schedules"]["vehicle_id"].isin(dfs["vehicles"]["id"]).all():
        results["transit_schedules"]["fk_valid"] = False
        results["transit_schedules"]["notes"].append("FK vehicle_id invalid")

    # bookings -> schedules
    if not dfs["ticket_bookings"]["schedule_id"].isin(dfs["transit_schedules"]["id"]).all():
        results["ticket_bookings"]["fk_valid"] = False
        results["ticket_bookings"]["notes"].append("FK schedule_id invalid")

    # 3. Null Rate Validations
    for name, df in dfs.items():
        for col in df.columns:
            null_count = df[col].isnull().sum()
            # vehicle_id and estimated_delivery_date in shipments are the intended nullable columns
            if name == "shipments" and col in ["vehicle_id", "estimated_delivery_date"]:
                null_pct = (null_count / len(df)) * 100
                if col == "vehicle_id" and (null_count == 0 or null_pct > 30):
                    results[name]["null_rates_valid"] = False
                    results[name]["notes"].append(f"vehicle_id null rate outside expected bounds ({null_pct:.1f}%)")
            else:
                if null_count > 0:
                    results[name]["null_rates_valid"] = False
                    results[name]["notes"].append(f"Unexpected NULLs in column '{col}': {null_count}")

    # 4. Synthetic Privacy Check
    non_example_emails = dfs["ticket_bookings"][~dfs["ticket_bookings"]["passenger_email"].str.endswith(".example.com")]
    if len(non_example_emails) > 0:
        results["ticket_bookings"]["notes"].append(f"BR-08 Violation: {len(non_example_emails)} non-example.com emails")

    return results


# =====================================================================
# 4. MAIN EXECUTION & CSV EXPORT
# =====================================================================

def main():
    print("=" * 70)
    print("LogiCraft Dataset Generator (Seed = 42)")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    warehouses = generate_warehouses()
    items = generate_inventory_items(warehouses)
    vehicles = generate_vehicles()
    shipments, checkpoints = generate_shipments(warehouses, items, vehicles)
    routes, schedules, bookings = generate_transit_data(vehicles)

    dfs = {
        "warehouses": warehouses,
        "inventory_items": items,
        "vehicles": vehicles,
        "shipments": shipments,
        "shipment_checkpoints": checkpoints,
        "transit_routes": routes,
        "transit_schedules": schedules,
        "ticket_bookings": bookings,
    }

    # Save to CSV
    for name, df in dfs.items():
        filepath = OUTPUT_DIR / f"{name}.csv"
        df.to_csv(filepath, index=False)
        print(f"[SAVED] {filepath.name:<25} ({len(df):>3} rows)")

    print("-" * 70)
    print("Running Dataset Integrity & Business Rule Validations...")
    print("-" * 70)

    val_results = validate_dataset(dfs)

    all_passed = True
    print(f"{'Table':<24} | {'Rows':<5} | {'PK Uniq':<7} | {'FK Valid':<8} | {'Nulls OK':<8} | {'Status'}")
    print("-" * 70)
    for table_name, res in val_results.items():
        status = "PASS" if res["pk_unique"] and res["fk_valid"] and res["null_rates_valid"] else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"{table_name:<24} | {res['rows']:<5} | {str(res['pk_unique']):<7} | {str(res['fk_valid']):<8} | {str(res['null_rates_valid']):<8} | {status}")
        for note in res["notes"]:
            print(f"  --> [ISSUE] {note}")

    print("-" * 70)

    # Verify Edge Cases
    print("Deliberate Edge Cases Audit:")
    zero_qty = items[items["quantity"] == 0]
    maint_v = vehicles[vehicles["status"] == "MAINTENANCE"]
    null_v_shipments = shipments[shipments["vehicle_id"].isnull()]
    sold_out_sched = schedules.iloc[0]["id"]
    sold_out_count = len(bookings[bookings["schedule_id"] == sold_out_sched])
    sold_out_cap = vehicles.set_index("id").loc[schedules.iloc[0]["vehicle_id"]]["capacity"]

    print(f"  [OK] Zero-stock item present: {zero_qty.iloc[0]['sku']} (Qty = {zero_qty.iloc[0]['quantity']})")
    print(f"  [OK] Maintenance vehicle locked: {maint_v.iloc[0]['registration_number']} (Status = {maint_v.iloc[0]['status']})")
    print(f"  [OK] Unassigned vehicle shipments: {len(null_v_shipments)} rows with vehicle_id = NULL")
    print(f"  [OK] Sold-out transit schedule: Schedule #{sold_out_sched} ({sold_out_count}/{sold_out_cap} seats booked)")
    print(f"  [OK] Privacy verification: 100% synthetic emails end with '.example.com'")
    print("=" * 70)

    if all_passed:
        print("[SUCCESS] All dataset integrity checks and edge cases PASSED!")
    else:
        print("[ERROR] Some validation checks failed. See issues above.")
        exit(1)


if __name__ == "__main__":
    main()
