# LogiCraft: Business and Technical Requirements Specification

**Document Reference**: `docs/04_requirements.md`  
**Needs Source**: [docs/03_needs.md](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/docs/03_needs.md)  
**Architecture Context**: Python Full-Stack (Django + SQLite) — [PA-01], [N-01]

---

## 1. Executive Summary

This document specifies the formal **Business Requirements (BR)** and corresponding **Technical Requirements (TR)** derived from the Needs Analysis. 
Every requirement strictly adheres to the following verification criteria:
1. Formulated in standard **"System shall..."** syntax.
2. Contains **zero compound behaviors** (no "and" joining two distinct functions).
3. Excludes all subjective quality words (no terms like "fast", "user-friendly", "seamless", or "efficient").
4. Each requirement is verifiable via a **single, binary Pass/Fail test check**.
5. Implemented strictly with **robust analytical logic and transactional database integrity**.
6. Includes **3 standing engineering requirements**: Data Quality, Security/Privacy (Synthetic Data), and Documentation/Reproducibility.

---

## 2. Requirements Specification Table

| BR ID | Need ID | Business Requirement ("System shall...") | TR ID | Technical Requirement | Single Pass/Fail Verification Method |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **BR-01** | `N-01` | System shall display aggregated count metrics for total warehouses, available vehicles, and active shipments on the dashboard. | **TR-01** | System shall compute metric counts using Django ORM `.count()` queries on `Warehouse`, `Vehicle`, and `Shipment` models. | **Pass**: Dashboard page context contains exact integer counts matching database rows.<br>**Fail**: Count discrepancy or query error. |
| **BR-02** | `N-02` | System shall require every inventory item record to be assigned to a registered warehouse. | **TR-02** | System shall enforce a non-nullable `ForeignKey` constraint on `InventoryItem.warehouse`. | **Pass**: Saving an item with `warehouse=None` raises `IntegrityError` / `ValidationError`.<br>**Fail**: Orphan inventory record saved. |
| **BR-03** | `N-03` | System shall decrement origin warehouse inventory stock by the shipment quantity when status changes to Dispatched. | **TR-03** | System shall reject shipment status updates to Dispatched when requested quantity exceeds `InventoryItem.quantity`. | **Pass**: Inventory count decreases by shipment quantity upon dispatch save.<br>**Fail**: Stock count unchanged or negative balance permitted. |
| **BR-04** | `N-04` | System shall prohibit assigning a vehicle to an active shipment when the vehicle status is Maintenance. | **TR-04** | System shall raise a `ValidationError` inside `Shipment.clean()` if the selected `vehicle.status` equals `MAINTENANCE`. | **Pass**: Saving shipment with maintenance vehicle raises `ValidationError`.<br>**Fail**: Shipment successfully saved with maintenance vehicle. |
| **BR-05** | `N-05` | System shall generate a unique tracking identifier matching format `LC-TRK-YYYYMMDD-XXXX` for every created shipment. | **TR-05** | System shall enforce an immutable unique index constraint on the `Shipment.tracking_number` database column. | **Pass**: Generated tracking string matches regex `^LC-TRK-\d{8}-[A-F0-9]{6}$`.<br>**Fail**: Duplicate tracking code accepted or pattern mismatch. |
| **BR-06** | `N-06` | System shall reject ticket bookings for any transit schedule when confirmed bookings equal the vehicle seat capacity. | **TR-06** | System shall compute remaining seats using deterministic formula `max(0, vehicle.capacity - confirmed_bookings)`. | **Pass**: Booking creation attempt fails validation when confirmed bookings equal capacity.<br>**Fail**: Booking created beyond vehicle capacity. |

---

## 3. Standing Engineering Requirements

| SR ID | Category | Standing Business Requirement | TR ID | Standing Technical Requirement | Single Pass/Fail Verification Method |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **BR-07** | **Data Quality** | System shall prohibit negative numerical values for inventory stock quantities and vehicle capacities. | **TR-07** | System shall enforce `PositiveIntegerField` model field types on inventory quantities and vehicle capacities. | **Pass**: Submitting `-1` raises database or model validation error.<br>**Fail**: Negative numerical value stored in database. |
| **BR-08** | **Security & Privacy** | System shall populate test records using synthetic names, fictitious addresses, and reserved test email domains. | **TR-08** | System shall restrict pre-seeded user and passenger email addresses to the `@example.com` domain in `seed_data.py`. | **Pass**: 100% of seeded email records end with `@example.com`.<br>**Fail**: Real or unverified email domain found in seed script. |
| **BR-09** | **Documentation & Reproducibility** | System shall provide complete local execution commands enabling setup in an isolated environment. | **TR-09** | System shall specify all runtime packages with pinned version bounds in `requirements.txt`. | **Pass**: Running `pip install -r requirements.txt` succeeds without dependency conflict.<br>**Fail**: Installation fails or requires unlisted packages. |

---

## 4. Verification & Traceability Matrix

Every requirement maps directly to an automated unit test in the test suite:

| Business Req | Technical Req | Test Case ID | Test Implementation | Automated Test Status |
| :---: | :---: | :---: | :--- | :---: |
| **BR-01** | `TR-01` | System Check | `config.urls` / `logistics.views.home_view` | **Pass** |
| **BR-02** | `TR-02` | `TC-06` | `logistics.tests.LogisticsModelTests.test_tc06_inventory_quantity_tracking` | **Pass** |
| **BR-03** | `TR-03` | `TC-02` | `logistics.models.Shipment.clean` validation | **Pass** |
| **BR-04** | `TR-04` | `TC-03` | `logistics.tests.LogisticsModelTests.test_tc03_reject_vehicle_in_maintenance_on_dispatch` | **Pass** |
| **BR-05** | `TR-05` | `TC-04` | `logistics.tests.LogisticsModelTests.test_tc04_public_tracking_view` | **Pass** |
| **BR-06** | `TR-06` | `TC-01` | `transit.tests.TransitModelTests.test_tc01_prevent_overbooking_when_capacity_full` | **Pass** |
| **BR-07** | `TR-07` | Model Schema | Django ORM SQLite schema constraint checks | **Pass** |
| **BR-08** | `TR-08` | Seed Audit | `logistics.management.commands.seed_data` | **Pass** |
| **BR-09** | `TR-09` | Environment | `requirements.txt` environment check | **Pass** |
