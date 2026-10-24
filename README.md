# LogiCraft: Logistics & Fleet Management System

> **A Comprehensive Python Full-Stack Enterprise Operations Platform**  
> *Fleet Tracking &bull; Multi-Depot Warehouse Inventory &bull; Outbound Shipment Manifesting &bull; Public Transit Timetables & Ticketing*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0.14-success.svg)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Frontend](https://img.shields.io/badge/Frontend-Bootstrap_5.3%20%7C%20Vanilla_JS-purple.svg)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Automated_Tests-33%20Passed%20(100%25)-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/Architecture-Modular_Monolith-informational.svg)](DEVELOPER.md)

---

## 1. Executive Project Overview

### 1.1 The Operational Challenge
Regional freight operators and suburban transport services frequently rely on disconnected spreadsheets and manual phone calls. This operational fragmentation causes three chronic failures:
1. **Multi-Depot Blind Spots (`PA-01`)**: Executive directors cannot assess live stock levels across regional warehouses without waiting for end-of-day reports.
2. **Double-Promising Phantom Stock (`PA-03`)**: Outbound orders fail to immediately decrement on-hand inventory, resulting in stock deficits.
3. **Unroadworthy Trip Assignments (`PA-04`)**: Vehicles currently undergoing maintenance are accidentally assigned to active freight routes.
4. **Commuter Bus Overbooking (`PA-06`)**: Unconstrained passenger ticket sales cause passengers to be stranded at terminals.

### 1.2 The LogiCraft Solution
LogiCraft unifies freight logistics and passenger transit operations into a high-cohesion, server-rendered Django application. Every business decision—from inventory allocation and vehicle dispatch to seat reservation—is strictly executed with high reliability and data integrity.

### 1.3 Key Traceability Identifiers
* **Pain Areas**: `PA-01` to `PA-06` ([docs/02_pain_areas.md](docs/02_pain_areas.md))
* **Stakeholder Needs**: `N-01` to `N-06` ([docs/03_needs.md](docs/03_needs.md))
* **Business Requirements**: `BR-01` to `BR-09` ([docs/04_requirements.md](docs/04_requirements.md))
* **Technical Requirements**: `TR-01` to `TR-09` ([docs/04_requirements.md](docs/04_requirements.md))
* **User Stories**: `US-01` to `US-07` ([docs/06_user_stories.md](docs/06_user_stories.md))
* **Test Cases**: `TC-01` to `TC-07` ([docs/07_test_cases.md](docs/07_test_cases.md))
* **Wireframe Screens**: `SCR-01` to `SCR-07` ([docs/wireframe.html](docs/wireframe.html))

---

## 2. Technology Stack & Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    CLIENT BROWSER                                       |
|  Bootstrap 5.3.3 UI  |  Chart.js 4.4 Dashboards  |  Vanilla JS Validation & Spinners   |
+--------------------------------------------+--------------------------------------------+
                                             | HTTP Requests (MVT Server-Rendered)
                                             v
+-----------------------------------------------------------------------------------------+
|                               DJANGO 5.0 MONOLITH BACKEND                               |
|                                                                                         |
|  logistics/ app                            transit/ app                                 |
|  - home_view (KPIs & Charts [BR-01])       - transit_schedules_view (Search [BR-06])    |
|  - shipment_dispatch_view ([BR-03, BR-04]) - book_ticket_view (Capacity Gate [BR-06])   |
|  - track_shipment_view ([BR-05])           - TicketBooking & TransitSchedule Models     |
|  - login_view & register_view ([BR-08])                                                 |
|                                                                                         |
|  Transactional Core (TR-02): transaction.atomic() & select_for_update() row locking    |
+--------------------------------------------+--------------------------------------------+
                                             | Enforced Foreign Keys & Constraints
                                             v
+-----------------------------------------------------------------------------------------+
|                                   SQLITE3 DATABASE                                      |
|  Warehouses | InventoryItems | Vehicles | Shipments | Checkpoints | Routes | Bookings   |
+-----------------------------------------------------------------------------------------+
```

* **Backend**: Python 3.10+ / Django `5.0.14`
* **Database**: SQLite3 with strict relational foreign keys and non-negative field constraints
* **Frontend**: Django Template Language (DTL) + Bootstrap `5.3.3` + Bootstrap Icons `1.11.3` + Chart.js `4.4.1` (Zero Node.js build pipelines)
* **Synthetic Data Generation**: `pandas`, `numpy`, `Faker` (Fixed random seed: `42`)
* **Test Automation**: Django `TestCase` (`unittest`) / `pytest`

---

## 3. Clean-Machine Installation & Execution Runbook

Follow these instructions to set up, populate, and run the project from a fresh terminal.

### Step 1: Clone or Open Project Repository
```powershell
cd C:\Users\KAIN\OneDrive\Desktop\logicraft
```

### Step 2: Create and Activate Virtual Environment
* **On Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
* **On macOS / Linux (Bash)**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Pinned Dependencies (`BR-09`)
```powershell
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```powershell
python manage.py migrate
```

### Step 5: Generate Synthetic Dataset (Reproducible Seed 42)
```powershell
python src/generate_data.py
```
*Generates 8 relational CSV files in `data/` and validates 100% primary/foreign key consistency.*

### Step 6: Load Dataset into SQLite Database
```powershell
python manage.py load_csv_data
```
*Ingests Warehouses, Inventory Items, Fleet Vehicles, Shipments, Checkpoints, Transit Routes, Schedules, and Bookings.*

### Step 7: Launch Local Development Server
```powershell
python manage.py runserver
```
Open your web browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 4. Pre-Configured Demo Credentials

The database is pre-seeded with authorized accounts for evaluating user roles:

| Role | Username | Password | Access Level | Primary Screen |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` | Full Superuser & Staff Admin | [`/admin/`](http://127.0.0.1:8000/admin/) |
| **Fleet Dispatcher** | `dispatcher_demo` | `Password123` | Operational Staff Access | [`/shipments/dispatch/`](http://127.0.0.1:8000/shipments/dispatch/) |
| **Public Customer / Commuter** | *No login needed* | *N/A* | Anonymous Public Access | [`/track/`](http://127.0.0.1:8000/track/) & [`/transit/`](http://127.0.0.1:8000/transit/) |

---

## 5. Feature Tour & Demonstration Workflows

### 5.1 Executive Operations Performance Dashboard (`/`)
* **Linked Requirements**: `US-01`, `BR-01`, `TR-01`
* **Features**:
  * 4 Live KPI Cards displaying aggregated warehouse counts, on-hand units, fleet readiness ratio, and active dispatches.
  * Interactive **Chart.js Depot Stock Bar Chart** reflecting 8 regional distribution hubs.
  * Interactive **Chart.js Fleet Allocation Donut Chart** highlighting available vs. maintenance assets.
  * Actionable warning banners for low-stock SKUs ($\le 3$ units) and vehicles undergoing maintenance.
  * Live feed of the 8 most recent dispatches and waypoint scan events.

### 5.2 Outbound Shipment Dispatch & Stock Decrement (`/shipments/dispatch/`)
* **Linked Requirements**: `US-03`, `US-04`, `BR-02`, `BR-03`, `BR-04`, `TR-02`, `TR-03`
* **Features**:
  * **Dynamic Stock Meter**: Selecting an SKU immediately updates a stock availability pill (`Available: 45 units`).
  * **Zero Over-Allocation Guard (`BR-03`)**: Rejects order quantities exceeding on-hand inventory; warns user in real time.
  * **Depot Consistency Check (`BR-02`)**: Guarantees that selected SKUs physically reside in the selected origin warehouse depot.
  * **Fleet Maintenance Lockout (`BR-04`)**: Prohibits assigning any vehicle in `MAINTENANCE` status; shows visual warning.
  * **Atomic Execution (`TR-02`)**: Wrapped in `transaction.atomic()`—deducts inventory, sets vehicle to `IN_TRANSIT`, generates a tracking number (`LC-TRK-YYYYMMDD-XXXX`), and logs an initial waypoint scan in a single commit.
  * **Anti-Duplicate Lock**: Disables the submit button and displays a loading spinner on submission.

### 5.3 Public Cargo Tracking & Checkpoint Timeline (`/track/`)
* **Linked Requirements**: `US-05`, `BR-05`, `TR-05`
* **Features**:
  * Public query input supporting parcel tracking codes (e.g. `LC-TRK-20261010-DEMO01`).
  * Visual 4-stage milestone stepper (`Pending` $\rightarrow$ `Dispatched` $\rightarrow$ `In Transit` $\rightarrow$ `Delivered`).
  * Chronological physical scan waypoint timeline displaying timestamps, hub locations, and handling notes.
  * Friendly "Tracking Number Not Found" error banner for unmanifested inquiries.

### 5.4 Transit Timetables & Capacity-Capped Booking (`/transit/`)
* **Linked Requirements**: `US-06`, `BR-06`, `TR-06`
* **Features**:
  * Route search filtering by origin stop and destination terminal.
  * Real-time seat calculation: $\text{Remaining Seats} = \max(0, \text{Vehicle Capacity} - \text{Confirmed Bookings})$.
  * **Sold-Out Lockout (`BR-06`)**: Replaces the booking action with a disabled "Sold Out" badge when remaining seats equal 0.
  * Ticket reservation receipt generating unique reference `LC-TKT-YYYYMMDD-XXXX` with dedicated print styling (`@media print`).

### 5.5 Staff Authentication & Access Control (`/accounts/`)
* **Linked Requirements**: `BR-08`, `TR-03`
* **Features**:
  * Staff Sign-In (`/accounts/login/`) with show/hide password toggle, username preservation on failure, and demo credential fill helper.
  * Staff Registration (`/accounts/register/`) with role assignment (`DIRECTOR`, `SUPERVISOR`, `DISPATCHER`), real-time password matching validation, and automatic `is_staff` provisioning.

### 5.6 Warehouse Inventory Cataloging (`/inventory/`)
* **Linked Requirements**: `US-02`, `BR-02`, `SCR-03`
* **Features**:
  * Multi-depot stock catalog browsing with real-time filters by regional facility and SKU category.
  * Instant search across product names and SKU codes.
  * Stock volume indicators with visual health badges (In-Stock, Low-Stock, and Out-of-Stock).
  * Direct 1-click dispatch navigation and staff restocking links.

---

## 6. Verification & Automated Test Suite

LogiCraft includes **33 automated unit, integration, and user-journey tests** providing complete code and rule coverage.

### Execute All Automated Tests
```powershell
python manage.py test logistics transit tests -v 2
```

### Expected Output
```text
Creating test database for alias 'default'...
Found 33 test(s).
System check identified no issues (0 silenced).
.................................
----------------------------------------------------------------------
Ran 33 tests in 3.075s

OK
Destroying test database for alias 'default'...
```

### Test Suite Structure

| Test File | Test Class | Coverage & Verified Rules | Scenarios |
| :--- | :--- | :--- | :---: |
| [`tests/test_journeys.py`](tests/test_journeys.py) | `DispatcherCargoLifecycleJourneyTests` | End-to-end freight dispatch: auth $\rightarrow$ form $\rightarrow$ atomic deduction $\rightarrow$ tracking stepper $\rightarrow$ dashboard metric update (`BR-01`, `BR-03`, `BR-04`, `BR-05`). | 1 |
| [`tests/test_journeys.py`](tests/test_journeys.py) | `CommuterTransitTicketingJourneyTests` | End-to-end transit booking: search $\rightarrow$ seat availability formula $\rightarrow$ sequential reservations $\rightarrow$ sold-out capacity saturation lockout (`BR-06`). | 1 |
| [`tests/test_journeys.py`](tests/test_journeys.py) | `EdgeCasesAndFailureResilienceJourneyTests` | Boundary failures: stock deficit rejection (`BR-03`), maintenance lockout (`BR-04`), duplicate seat conflict, 404 handler, and synthetic email domain audit (`BR-08`). | 7 |
| [`tests/test_dispatch_form.py`](tests/test_dispatch_form.py) | `ShipmentDispatchFormTests` | Form validation: depot matching (`BR-02`), deficit rejection (`BR-03`), non-positive quantities (`BR-07`), and pending manifest holding. | 7 |
| [`tests/test_system.py`](tests/test_system.py) | `AuthSystemTests` & `SystemSmokeTests` | Staff login/register/logout workflows, role granting, credential preservation, and baseline endpoint smoke tests. | 12 |
| [`logistics/tests.py`](logistics/tests.py) | `LogisticsModelTests` | Model constraints, maintenance lockout on save, and inventory stock increments. | 3 |
| [`transit/tests.py`](transit/tests.py) | `TransitModelTests` | Seat remaining formula calculation and overbooking prevention at model level. | 2 |
| **Total** | | | **33 / 33 Passed** |

---

## 7. Complete Documentation Suite Index

All project engineering artifacts are maintained in the [`docs/`](docs/) directory:

| Document | Description |
| :--- | :--- |
| [`docs/01_stakeholders.md`](docs/01_stakeholders.md) | Profiles, operational concerns, and decision authority for 4 key roles. |
| [`docs/02_pain_areas.md`](docs/02_pain_areas.md) | Detailed analysis of shortlisted operational pain areas (`PA-01` to `PA-06`). |
| [`docs/03_needs.md`](docs/03_needs.md) | Needs formulation, solution-trap critique, and top-3 "How Might We" questions. |
| [`docs/04_requirements.md`](docs/04_requirements.md) | Atomic Business (`BR-01` to `BR-09`) and Technical (`TR-01` to `TR-09`) requirements. |
| [`docs/05_traceability.md`](docs/05_traceability.md) | End-to-end traceability matrix, MoSCoW prioritization, and approved MVP definition. |
| [`docs/06_user_stories.md`](docs/06_user_stories.md) | Agile user story catalog (`US-01` to `US-07`) with Given/When/Then acceptance criteria. |
| [`docs/07_test_cases.md`](docs/07_test_cases.md) | Formal test verification matrix (`TC-01` to `TC-07`) with exact assertions. |
| [`docs/08_architecture_tech_stack.md`](docs/08_architecture_tech_stack.md) | Architecture comparison (Django vs. FastAPI), trade-offs, and full-stack engineering domains. |
| [`docs/09_data_design.md`](docs/09_data_design.md) | Relational database architecture, Mermaid ER diagram, full 8-table data dictionary, and edge-case dataset seeds. |
| [`docs/10_backend_integration.md`](docs/10_backend_integration.md) | Master screen-to-backend operations mapping, sequence diagrams, and transaction contracts. |
| [`docs/wireframe.html`](docs/wireframe.html) | Self-contained, interactive low-fidelity grayscale wireframe covering all 7 screens. |
| [`DEVELOPER.md`](DEVELOPER.md) | Developer master reference file detailing conventions, non-negotiable rules, and Definition of Done. |

---

## 8. Standing Engineering Standards Compliance

* **`BR-07` Data Quality**: 100% of quantity and capacity fields utilize `models.PositiveIntegerField`, mathematically preventing negative balances at the database layer.
* **`BR-08` Security & Privacy**: All pre-seeded and test user accounts strictly utilize the reserved RFC test domain `@example.com`. No personal identifying information (PII) exists in seed scripts.
* **`BR-09` Reproducibility**: All runtime dependencies are pinned with exact version bounds in [`requirements.txt`](requirements.txt), guaranteeing identical execution across fresh environments.
* **Strict Data Integrity**: All routing, scheduling, inventory decrement, and validation operations are enforced via ACID transactional guarantees in Python and Django ORM.
