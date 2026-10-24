# Project Synopsis — Submission Document
### HCLTech Career Shaper Programme | III Year Industry Project | 2025-26

---

## Candidate & Project Identification Table

| Field | Details (Learner to complete) |
| :--- | :--- |
| **Project Title** | **LogiCraft: Integrated Logistics & Fleet Management System** |
| **Project No.** | 69 |
| **Domain** | Full Stack / Python |
| **Difficulty** | Intermediate |
| **Duration** | 4 Weeks |
| **Format** | Individual Project |
| **Learner Name** | Alisha |
| **Roll Number** | [FILL IN] |
| **College / Campus** | [FILL IN] |
| **Mentor Name** | [FILL IN] |
| **Submission Date** | 24 October 2026 |
| **GitHub Repository URL** | [https://github.com/alisha-30/Logicraft.git](https://github.com/alisha-30/Logicraft.git) |

---

## 1. Problem Statement

Regional freight operators and suburban commuter services struggle with operational fragmentation caused by disconnected spreadsheets and manual phone logs (**Who/Where**). 

This lack of real-time synchronization leads to three critical operational failures during daily dispatch and scheduling (**When/What**):
1. Accidental assignment of unroadworthy vehicles currently undergoing workshop maintenance.
2. Inventory stock deficits and "phantom inventory" caused by outbound deliveries not decrementing depot balances immediately.
3. Overbooking on municipal commuter routes resulting in stranded passengers at terminals (**Why**).

To solve this, a unified, transactional full-stack platform is required to mathematically enforce inventory decrements, maintenance lockout safeguards, and capacity-constrained ticket booking in real-time (**How**).

---

## 2. Proposed Solution & Approach

To resolve these operational bottlenecks, I designed and implemented **LogiCraft**, a unified enterprise web platform developed using **Python 3.10, Django 5.0, SQLite3, and Bootstrap 5.3**. 

The system unifies two high-impact domains into a shared operational core:
* **B2B Freight Logistics**: Manages 8 regional warehouse depots, tracks 80 catalog SKUs, enforces automatic stock deduction upon shipment manifesting, locks servicing vehicles from dispatch, and provides a public 4-step consignment tracking stepper.
* **B2C Public Commuter Transit**: Provides timetable search across municipal corridors, computes real-time remaining seat availability, and eliminates overbooking by capping reservations to vehicle capacity.

The solution ensures 100% data integrity through atomic database transactions (`transaction.atomic`) and is validated by a comprehensive suite of **33 automated unit and integration tests**.

---

## 3. System Architecture

### 3.1 Data Flow Diagram (DFD Level 0 — Context Level)

```text
  [ Warehouse Staff / Dispatcher ]          [ Public Consignee / Customer ]
              |                                          |
   (Dispatch Manifest / Stock Mgmt)              (Tracking Code Query)
              |                                          |
              v                                          v
      +------------------------------------------------------+
      |                                                      |
      |       LOGICRAFT: UNIFIED ENTERPRISE PLATFORM         |
      |        (Django 5.0 MVT Full-Stack Architecture)      |
      |                                                      |
      +------------------------------------------------------+
              ^                                          |
              |                                  (Enforce Constraints)
      (Browse Routes / Book Seat)                        |
              |                                          v
      [ Public Transit Commuter ]            +-----------------------+
                                             |  SQLite3 Database     |
                                             |  (8 Normalized Tables)|
                                             +-----------------------+
```

### 3.2 System Block Diagram

```text
+-----------------------------------------------------------------------------------+
|                            PRESENTATION LAYER (UI)                                |
|  Bootstrap 5.3 Responsive Views • Chart.js Metrics • 4-Step Parcel Tracking Stepper |
+-----------------------------------------------------------------------------------+
                                         │  HTTP Requests / Form Submissions
                                         ▼
+-----------------------------------------------------------------------------------+
|                        APPLICATION & BUSINESS LOGIC LAYER                         |
|                                                                                   |
|  [ logistics App ]                                [ transit App ]                 |
|  - Operations Dashboard (`/`)                     - Route Timetables (`/transit/`)|
|  - Inventory Catalog (`/inventory/`)              - Dynamic Seat Availability     |
|  - Outbound Dispatch (`/shipments/dispatch/`)     - Capacity Validation Engine    |
|  - Public Parcel Tracker (`/track/`)              - Instant Ticket Confirmation   |
|                                                                                   |
|  [ Core Safeguard Rules ]                                                         |
|  * Inventory Deficit Lockout   * Maintenance Fleet Lockout   * Atomic Rollback    |
+-----------------------------------------------------------------------------------+
                                         │  Django ORM Queries / ACID Transactions
                                         ▼
+-----------------------------------------------------------------------------------+
|                             DATABASE STORAGE LAYER                                |
|  SQLite3 Relational Database (3NF Normalized, 8 Tables, Foreign Key Constraints)  |
|  * Warehouses   * InventoryItems   * Vehicles   * Shipments   * Checkpoints       |
|  * TransitRoutes   * TransitSchedules   * TicketBookings                          |
+-----------------------------------------------------------------------------------+
```

---

## 4. Technology Stack

| Layer | Selected Technology | Version / Specification | Purpose & Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend / UI** | HTML5, CSS3, Bootstrap | `5.3.3` | Clean, mobile-responsive enterprise interface with zero Node.js/npm dependencies. |
| **Backend / Logic** | Python, Django | `Python 3.10+`, `Django 5.0.x` | High-cohesion MVT architecture, secure ORM, form validation, and session handling. |
| **Database** | SQLite3 | `Native` | Relational 3NF architecture with 8 tables and enforced Foreign Key constraints. |
| **AI/ML Framework** | N/A (Rule-Based Engine) | `None` | Pure deterministic transactional business logic, eliminating opaque failure points. |
| **Visualisation** | Chart.js & Bootstrap Icons | `4.x CDN` | Interactive depot stock bar charts and fleet allocation donut charts. |
| **Hardware** | Standard PC / Laptop | Minimum: 4GB RAM, Core i3 | Zero specialized hardware required; runs 100% locally on localhost. |

---

## 5. Dataset Used

* **Dataset File Names**: Exported relational datasets located in `data/`:
  1. `warehouses.csv`
  2. `inventory_items.csv`
  3. `vehicles.csv`
  4. `shipments.csv`
  5. `shipment_checkpoints.csv`
  6. `transit_routes.csv`
  7. `transit_schedules.csv`
  8. `ticket_bookings.csv`
* **Number of Rows**: **416 total relational records** across all 8 tables:
  * 8 Regional Warehouses
  * 80 Inventory SKUs
  * 25 Fleet Vehicles
  * 50 Shipments & 99 Transit Checkpoints
  * 8 Transit Routes, 24 Departure Schedules, and 120 Passenger Bookings
* **Number of Columns**: 8 relational tables featuring **4 to 12 normalized columns per entity**.
* **Key Columns (Top 5)**:
  1. `tracking_number` (Unique shipment identifier matching `LC-TRK-YYYYMMDD-XXXX`)
  2. `sku` (Stock Keeping Unit unique code, e.g., `SKU-SOL-101`)
  3. `quantity` (On-hand warehouse inventory balance, constrained to $\ge 0$)
  4. `status` (Vehicle operational state: `AVAILABLE`, `IN_TRANSIT`, `MAINTENANCE`)
  5. `seat_number` (Allocated passenger seat index constrained to vehicle capacity)
* **Any Additional Data Collected**: **None**. 100% synthetic, benchmarked data generated via Python `pandas`, `numpy`, and `Faker` using deterministic `seed=42`. All email records strictly adhere to the reserved RFC 2606 test domain (`@example.com`), ensuring **Zero Personally Identifiable Information (PII)** leakage.

---

## 6. Key Results & Metrics

* **Metric 1: Automated Test Suite Reliability**: **33 / 33 Tests Passed (100% Pass Rate)** with zero errors or warnings (`Ran 33 tests in 5.1s: OK`).
* **Metric 2: Local Transaction & Query Response Time**: **< 45 milliseconds** average response time across database reads, form validations, and template rendering.
* **Metric 3: Inventory Deficit & Overbooking Rate**: **0% (Zero)**. The system mathematically prevents negative stock balances and rejects 100% of booking attempts exceeding vehicle seating capacity.
* **Business Value Achieved**:
  1. Consolidated two fragmented operations (Freight + Passenger Transit) into a single unified platform.
  2. Eliminated human error in dispatching vehicles under repair through automated status lockout.
  3. Provided complete customer visibility via a public 4-step consignment progress tracker.

---

## 7. Challenges Faced & How Resolved

* **Challenge 1: Transactional Concurrency & Stock Desynchronization**:
  * *Problem*: During outbound shipment dispatch, multiple database records must be altered simultaneously (generating shipment manifest, decrementing warehouse SKU quantity, creating the initial tracking checkpoint, and updating vehicle state). If any intermediate step failed, partial writes corrupted stock levels.
  * *Resolution*: Encapsulated the entire dispatch workflow inside Django's `with transaction.atomic():` context manager. If any validation or database exception occurs, Django automatically rolls back all changes, guaranteeing ACID compliance and zero orphan records.

* **Challenge 2: Dynamic Transit Overbooking Prevention**:
  * *Problem*: Preventing passengers from reserving seats once a bus reached its physical capacity, without introducing heavy client-side polling or race conditions.
  * *Resolution*: Implemented a clean, model-level seat constraint formula: `remaining_seats = vehicle.capacity - confirmed_bookings`. In the booking view, bookings are confirmed inside an atomic check that verifies `remaining_seats > 0` before inserting the reservation. If zero seats remain, the route displays a "Sold Out" state and blocks form submission.

---

## 8. References

1. **Django Software Foundation**. (2024). *Django Documentation: Models, Transactions & Testing (Version 5.0)*. Available at: https://docs.djangoproject.com/
2. **Date, C. J.** (2019). *Database Design and Relational Theory: Normal Forms and All That Jazz (2nd Edition)*. O'Reilly Media.
3. **Python Software Foundation**. (2024). *The Python 3.10 Standard Library Reference*. Available at: https://docs.python.org/3.10/
4. **Bootstrap Team**. (2024). *Bootstrap 5.3: Components, Layout and Responsive Grid System*. Available at: https://getbootstrap.com/
5. **Internet Engineering Task Force (IETF)**. (1999). *RFC 2606: Reserved Top Level DNS Names for Testing & Documentation*. Available at: https://www.rfc-editor.org/rfc/rfc2606

---

## 9. Ethical Compliance Declaration

I confirm that:
- [x] All dataset usage complies with the source licence (100% synthetic, open-source generated).
- [x] No personally identifiable information (PII) is stored without consent (all identities use synthetic names and reserved `@example.com` domains).
- [x] All development standards and architectural integrity rules have been strictly maintained.
- [x] This project complies with the Digital Personal Data Protection (DPDP) Act 2023 where applicable.

<br>

**Learner Signature**: Alisha &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date**: 24 October 2026

---
*Submit this file as `Project_Synopsis_Alisha_[RollNo].docx` | HCLTech Career Shaper Programme 2025-26*
