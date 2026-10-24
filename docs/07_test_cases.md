# LogiCraft: Comprehensive Test Specification & Verification Matrix

**Document Reference**: `docs/07_test_cases.md`  
**User Stories Source**: [docs/06_user_stories.md](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/docs/06_user_stories.md)  
**Requirements Source**: [docs/04_requirements.md](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/docs/04_requirements.md)  
**Automated Test Implementations**: [logistics/tests.py](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/logistics/tests.py) & [transit/tests.py](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/transit/tests.py)

---

## 1. Executive Summary

This document specifies the formal test cases verifying LogiCraft.
1. Every **MVP user story** includes **at least one Happy-Path test** and **at least one Invalid-Input/Edge test**.
2. All expected results are formulated with **exact, measurable assertions** (exact HTTP codes, database field values, or explicit exception types; never vague terms like *"works correctly"*).
3. Automated test feasibility using **`pytest` / Django `TestCase`** is explicitly noted for every scenario.
4. Includes **3 standing engineering tests**: Data Quality, Synthetic Privacy Audit, and Clean-Machine Reproducibility.

---

## 2. Test Cases Specification Table

| TC ID | US ID | BR ID | Scenario | Test Data | Steps | Expected Result (Exact) | Type | pytest Automatable? |
| :---: | :---: | :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC-01.1** | `US-01` | `BR-01` | Dashboard metrics render correct database totals | 3 Warehouses, 2 Available Vehicles, 4 Active Shipments | 1. Seed exact test records.<br>2. Execute HTTP GET on `/`. | HTTP 200; context `stats['total_warehouses'] == 3`, `stats['vehicles_available'] == 2`, `stats['shipments_active'] == 4`. | Happy Path | Yes (`client.get('/')`) |
| **TC-01.2** | `US-01` | `BR-01` | Dashboard renders cleanly with zero database rows | 0 Warehouses, 0 Vehicles, 0 Shipments | 1. Clear database tables.<br>2. Execute HTTP GET on `/`. | HTTP 200; context displays integers `0` across all metric cards without raising `ZeroDivisionError` or `AttributeError`. | Edge Case | Yes (`client.get('/')`) |
| **TC-02.1** | `US-02` | `BR-02` | Save inventory item associated with valid warehouse | Warehouse `WH-01`, SKU `SKU-SOL-101`, Qty `25` | 1. Create `Warehouse(code="WH-01")`.<br>2. Save `InventoryItem` with `warehouse=WH-01`. | `InventoryItem.objects.filter(sku="SKU-SOL-101").exists() == True`; foreign key `item.warehouse.code == "WH-01"`. | Happy Path | Yes (`InventoryItem.objects.create`) |
| **TC-02.2** | `US-02` | `BR-02` | Attempt to save inventory item without warehouse link | SKU `SKU-ORPHAN`, Qty `10`, Warehouse `None` | 1. Instantiate `InventoryItem(sku="SKU-ORPHAN", warehouse=None)`.<br>2. Call `item.full_clean()`. | Raises `django.core.exceptions.ValidationError` containing key `'warehouse'` with message `"This field cannot be null"`. | Invalid Input | Yes (`pytest.raises(ValidationError)`) |
| **TC-03.1** | `US-03` | `BR-03` | Deduct stock upon valid shipment dispatch | Item stock = `20`, Shipment qty = `5` | 1. Create stock of 20.<br>2. Update shipment status to `DISPATCHED` with qty 5. | `InventoryItem.objects.get(id=...).quantity == 15`; `Shipment.status == "DISPATCHED"`. | Happy Path | Yes (Model method test) |
| **TC-03.2** | `US-03` | `BR-03` | Reject dispatch when requested quantity exceeds available stock | Item stock = `3`, Shipment qty = `10` | 1. Create stock of 3.<br>2. Attempt to transition shipment of 10 to `DISPATCHED`. | Transaction rejected; raises `ValidationError`; database item quantity remains unchanged at `3`. | Invalid Input | Yes (`pytest.raises(ValidationError)`) |
| **TC-04.1** | `US-04` | `BR-04` | Assign available vehicle to outgoing cargo | Vehicle status = `AVAILABLE`, Shipment status = `DISPATCHED` | 1. Create vehicle with `status='AVAILABLE'`.<br>2. Assign to shipment and call `shipment.full_clean()`. | Validation succeeds with 0 errors; `shipment.vehicle == vehicle`. | Happy Path | Yes (`full_clean()`) |
| **TC-04.2** | `US-04` | `BR-04` | Reject assigning vehicle currently under maintenance | Vehicle status = `MAINTENANCE`, Shipment status = `DISPATCHED` | 1. Create vehicle with `status='MAINTENANCE'`.<br>2. Assign to shipment and call `shipment.full_clean()`. | Raises `ValidationError` containing message: `"is under maintenance and cannot be assigned"`. | Invalid Input | Yes (`pytest.raises(ValidationError)`) |
| **TC-05.1** | `US-05` | `BR-05` | Public query for valid tracking code | Tracking code `LC-TRK-20261010-DEMO01` | 1. Seed shipment and checkpoints.<br>2. Execute HTTP GET on `/track/?q=LC-TRK-20261010-DEMO01`. | HTTP 200; response body contains string `"LC-TRK-20261010-DEMO01"` and rendered milestone stepper. | Happy Path | Yes (`client.get('/track/')`) |
| **TC-05.2** | `US-05` | `BR-05` | Public query for non-existent tracking code | Tracking code `INVALID-999-XYZ` | 1. Execute HTTP GET on `/track/?q=INVALID-999-XYZ`. | HTTP 200; context `not_found == True`; response body contains string `"Tracking Number Not Found"`. | Invalid Input | Yes (`client.get('/track/')`) |
| **TC-06.1** | `US-06` | `BR-06` | Book transit ticket on route with available seats | Bus Capacity = `30`, Confirmed = `0`, Seat = `1` | 1. Create schedule.<br>2. Execute HTTP POST to `/transit/book/<id>/` with passenger name and seat 1. | HTTP 200; `TicketBooking.objects.count() == 1`; response body displays booking reference starting with `"LC-TKT-"`. | Happy Path | Yes (`client.post()`) |
| **TC-06.2** | `US-06` | `BR-06` | Reject booking when bus capacity is full | Bus Capacity = `2`, Confirmed = `2`, Remaining = `0` | 1. Fill bus capacity to 2.<br>2. Execute HTTP POST to `/transit/book/<id>/` for seat 3. | Booking rejected; returns error message containing `"currently sold out"`; database confirmed count remains `2`. | Edge Case | Yes (`client.post()`) |
| **TC-07.1** | `US-07` | `BR-07` | Positive quantity accepted in inventory model | Qty = `100`, Capacity = `5000` | 1. Save `InventoryItem(quantity=100)`. | Record saved successfully; `item.quantity == 100`. | Happy Path | Yes (Model test) |
| **TC-07.2** | `US-07` | `BR-07` | Reject negative integer in inventory quantity | Qty = `-5` | 1. Instantiate `InventoryItem(quantity=-5)`.<br>2. Call `full_clean()`. | Raises `ValidationError` stating `"Ensure this value is greater than or equal to 0"`. | Invalid Input | Yes (`pytest.raises(ValidationError)`) |

---

## 3. Standing Engineering Tests

### [TC-STAND-01] Data Quality & Invariant Audit
* **Objective**: Verify that database schema enforces strictly positive values and cascade constraints.
* **Steps**:
  1. Inspect model fields across `logistics` and `transit`.
  2. Attempt to save negative quantities or orphan records.
* **Expected Result (Exact)**:
  * 100% of quantity and capacity fields utilize `models.PositiveIntegerField`.
  * Orphan item creation raises `IntegrityError` or `ValidationError`.
* **Automation**: Automatable via `pytest` running `python manage.py test`.

---

### [TC-STAND-02] Synthetic Data Privacy Audit
* **Objective**: Verify that no real personal names or proprietary email domains exist in project seed files.
* **Steps**:
  1. Execute `python manage.py seed_data`.
  2. Execute query: `TicketBooking.objects.exclude(passenger_email__endswith="@example.com")`.
* **Expected Result (Exact)**:
  * Query returns exactly `0` records.
  * 100% of seeded email addresses use the reserved RFC test domain `@example.com`.
* **Automation**: Automatable via `pytest` audit script.

---

### [TC-STAND-03] Clean-Machine Reproducibility Test (Run-From-README)
* **Objective**: Verify that an evaluator on a fresh computer can clone, configure, and launch the application using strictly the commands documented in `README.md`.
* **Steps**:
  1. Open a clean PowerShell window outside any active virtual environment.
  2. Run: `python -m venv .test_venv`
  3. Run: `.\.test_venv\Scripts\python.exe -m pip install -r requirements.txt`
  4. Run: `.\.test_venv\Scripts\python.exe manage.py test`
  5. Run: `.\.test_venv\Scripts\python.exe manage.py check`
* **Expected Result (Exact)**:
  * `pip install` completes with exit code `0`.
  * `manage.py test` executes all unit tests with output ending in `OK`.
  * `manage.py check` outputs: `"System check identified no issues (0 silenced)"`.
* **Automation**: Manual evaluator test or CI/CD script.

---

## 4. Test Execution Instructions

To execute the automated test cases in your project directory:

```powershell
# Using Django's built-in test runner
.\.venv\Scripts\python.exe manage.py test

# Or using pytest (if installed)
.\.venv\Scripts\pytest
```

Current test suite status in codebase: **5/5 tests passing with 0 errors (Ran in 0.074s)**.
