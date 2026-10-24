# LogiCraft: Software Requirements & Test Specification

Document Version: 1.0  
Status: Production Ready & Verified  
Stack: Python (Django) + SQLite + Bootstrap 5  
Architecture: Full-Stack Django Architecture

---

## 1. Project Approach & Delivery Plan

### [PA-01] Phased Delivery Plan (14-Day Sprint)
- **Phase 1 (Days 1–7): Core Logistics Foundation**
  - Database schema & Django Admin for Fleet, Warehouses, Inventory, and Shipments.
  - Dispatch workflows and public shipment tracking portal.
- **Phase 2 (Days 8–12): Public Transit & Ticketing**
  - Route definitions, vehicle scheduling, and seat reservation engine.
  - Commuter search & booking interface.
- **Phase 3 (Days 13–14): Quality Assurance & Verification**
  - Automated unit test suite execution (TC-01 to TC-06).
  - UI polish, test seed data, and comprehensive documentation.

---

## 2. Non-Functional Requirements & Constraints

### [N-01] System Constraints & Quality Attributes
- **N-01.1 (Data Integrity)**: System behavior must be entirely reliable with ACID transactional safety and schema validation.
- **N-01.2 (Portability)**: Must run locally on Python 3.10+ with an SQLite file database; no external cloud server or paid database setup needed.
- **N-01.3 (Zero Paid APIs)**: No paid mapping, SMS, or payment gateways. Public coordinates/checkpoints are handled internally or via open Leaflet/OpenStreetMap.
- **N-01.4 (Accessibility & Simplicity)**: Server-rendered templates (Django Templates + Bootstrap 5) without complex Node.js build pipelines.

---

## 3. Business Rules

### [BR-01] Shipment Lifecycle State Machine
A shipment must follow a strict, linear state progression:
$$\text{Pending} \longrightarrow \text{Dispatched} \longrightarrow \text{In Transit} \longrightarrow \text{Delivered}$$
*(A shipment may transition to `Cancelled` only from `Pending` or `Dispatched` state).*

### [BR-02] Inventory Depletion & Non-Negative Balance
When a shipment is marked `Dispatched`, the ordered quantity must be immediately decremented from the origin warehouse's `InventoryItem` stock. The system must reject any dispatch that causes stock to drop below zero.

### [BR-03] Vehicle Allocation Concurrency
A vehicle may only be assigned to an active shipment or transit route if its status is `Available`. Vehicles marked `In Transit` or `Maintenance` cannot be assigned.

### [BR-04] Transit Seat Capacity Enforcement
A public transit trip cannot accept bookings if:
$$\text{Confirmed Bookings} \ge \text{Vehicle Seat Capacity}$$
Remaining seats must be calculated as: $\text{Remaining Seats} = \text{Capacity} - \text{Bookings}$.

### [BR-05] Unique Tracking Code Standard
Every shipment must be assigned a unique, immutable tracking code upon creation in the format `LC-TRK-YYYYMMDD-XXXX` (where `XXXX` is a randomized alphanumeric suffix).

---

## 4. Technical Requirements

### [TR-01] Architecture & Technology Stack
- **Backend**: Django 4.2 LTS / 5.0 (Python 3.10+).
- **Database**: SQLite3 with foreign-key constraints enforced.
- **Frontend**: Django Template Language (DTL) + Bootstrap 5 + Vanilla JavaScript.

### [TR-02] Data Domain Entities
1. **Warehouse**: `name`, `code`, `address`, `capacity_sqft`.
2. **InventoryItem**: `warehouse_id` (FK), `sku`, `name`, `category`, `quantity`, `unit`.
3. **Vehicle**: `registration_number`, `vehicle_type` (Truck/Van/Bus), `capacity`, `status` (Available, In Transit, Maintenance).
4. **Shipment**: `tracking_number`, `origin_warehouse_id` (FK), `destination_address`, `vehicle_id` (FK, nullable), `status`, `created_at`.
5. **ShipmentCheckpoint**: `shipment_id` (FK), `timestamp`, `location_name`, `status_note`.
6. **TransitRoute**: `route_code`, `origin_stop`, `destination_stop`, `duration_minutes`.
7. **TransitSchedule**: `route_id` (FK), `vehicle_id` (FK), `departure_time`, `arrival_time`, `fare`.
8. **TicketBooking**: `schedule_id` (FK), `passenger_name`, `passenger_email`, `seat_number`, `booking_status`.

### [TR-03] Role-Based Access Control
- **Public Users**: Access public tracking search (`/track/`) and transit schedule lookup/booking (`/transit/`).
- **Staff / Dispatchers**: Authenticated access to Django dashboard and admin back-office to create shipments, manage inventory, and allocate vehicles.

---

## 5. User Stories

- **[US-01] Dispatcher Shipment Creation**:  
  *As a logistics dispatcher*, I want to create a shipment and assign an available vehicle so that the cargo can be officially routed.
- **[US-02] Warehouse Stock Management**:  
  *As a warehouse supervisor*, I want to record incoming stock shipments so that the inventory records accurately reflect physical warehouse contents.
- **[US-03] Public Cargo Tracking**:  
  *As a customer*, I want to enter my tracking number on the homepage without logging in so that I can see the timeline of my parcel.
- **[US-04] Fleet Maintenance Logging**:  
  *As a fleet manager*, I want to toggle a vehicle’s status to `Maintenance` so that dispatchers cannot accidentally assign it to a trip.
- **[US-05] Commuter Ticket Booking**:  
  *As a public commuter*, I want to search bus routes between two stops and book an available seat so that I secure my trip in advance.
- **[US-06] Transit Route Coordination**:  
  *As a transport coordinator*, I want to schedule a bus route for a specific departure time so that passengers can view and book tickets.

---

## 6. Test Cases & Verification Matrix

| Test ID | Associated Story | Test Objective | Execution Steps | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **[TC-01]** | US-05 | Prevent overbooking on transit route | 1. Identify schedule with 0 remaining seats.<br>2. Attempt to submit booking. | System returns error message: "Route fully booked"; no booking saved. |
| **[TC-02]** | US-01, US-02 | Prevent dispatch when inventory is insufficient | 1. Select item with quantity 5.<br>2. Attempt to dispatch shipment of 10 units. | Form validation error; transaction rejected; stock remains 5. |
| **[TC-03]** | US-01, US-04 | Prevent assigning unavailable vehicle | 1. Set Vehicle #1 to `In Transit`.<br>2. Attempt to assign Vehicle #1 to new shipment. | Vehicle #1 does not appear in active dropdown or raises validation error on save. |
| **[TC-04]** | US-03 | Public shipment tracking lookup | 1. Query valid tracking number `LC-TRK-...`.<br>2. Query non-existent tracking number `INVALID123`. | Valid query returns chronological checkpoint timeline (HTTP 200). Invalid query returns friendly "Tracking number not found" page. |
| **[TC-05]** | US-01 | Enforce sequential shipment state transitions | 1. Attempt to update a shipment directly from `Pending` to `Delivered`. | Rejected by model clean/validation method; status must pass through intermediate stages. |
| **[TC-06]** | US-02 | Inventory increment on restock | 1. Record restock of 20 units for an item with initial quantity 10. | Item quantity updates accurately to 30; inventory log entry recorded. |
