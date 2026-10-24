# LogiCraft: Shortlisted Pain Areas Specification

**Document Reference**: `docs/02_pain_areas.md`  
**Stakeholder Source**: [docs/01_stakeholders.md](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/docs/01_stakeholders.md)  
**Scope Context**: Python Full-Stack (Django + SQLite) — [PA-01], [N-01]

---

## 1. Executive Summary

This document formalizes the **6 shortlisted operational pain areas** selected under **Option 2 (Balanced Multi-Stakeholder Scope)**. Each pain area defines an observed operational bottleneck (a real-world problem, not a system feature) without fabricated statistical claims. Every pain area directly maps to a system business rule (**BR**) and automated verification test case (**TC**).

---

## 2. Shortlisted Pain Areas Matrix

| ID | Pain (A Problem, Not a Feature) | Stakeholder | Concrete Operational Evidence | Confirming Source | Severity | System Mitigation |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **PA-01** | Multi-depot operational blind spots due to fragmented offline reports | Operations Director | Management must wait for end-of-day emails from individual depots to know total active cargo volume. | End-of-day depot email chains and daily summary spreadsheets | **High** | Real-time aggregated operations dashboard (**TR-01**) |
| **PA-02** | Discrepancy between logged inventory counts and physical shelf stock | Warehouse Supervisor | Dispatchers request 10 units of an item for packing, but warehouse staff finds only 3 units physically in the bay. | Physical warehouse audit sheets and cancelled pick-lists citing missing items | **High** | Digital inventory ledger with per-warehouse stock counts (**US-02**, **TC-06**) |
| **PA-03** | Outbound shipments do not immediately decrement available inventory | Warehouse Supervisor | Two dispatchers allocate the same remaining batch of goods to different orders within the same afternoon. | Warehouse dispatch manifests compared against inventory ledger timestamps | **High** | Immediate stock decrement upon dispatch with non-negative validation (**BR-02**, **TC-02**) |
| **PA-04** | Vehicles undergoing maintenance are mistakenly assigned to active trips | Fleet Dispatcher | A driver arrives to take an assigned truck only to find mechanics have disassembled its brakes in the workshop. | Workshop repair job cards and dispatch re-assignment logs | **High** | Automatic exclusion of maintenance vehicles from active dispatch choices (**BR-03**, **TC-03**) |
| **PA-05** | Manual or duplicate tracking codes cause parcel lookup failures | Fleet Dispatcher | Customers inquire about tracking code "TRK-01", but two different customers were issued the identical reference code. | Customer support complaint logs and conflicting paper delivery receipts | **Medium** | Immutable, auto-generated unique tracking numbers (**BR-05**, **US-03**, **TC-04**) |
| **PA-06** | Bus overbooking and overcrowding due to lack of seating capacity enforcement | Public Commuter | Commuters purchase tickets at the terminal only to be denied boarding because all 30 seats are already taken. | Terminal customer complaint registers and conductor incident logs | **High** | Capacity-bounded ticket reservation engine (**BR-04**, **US-05**, **TC-01**) |

---

## 3. Detailed Pain Area Profiles & Traceability

### [PA-01] Multi-Depot Operational Blind Spots
* **Problem**: Logistics operations rely on siloed spreadsheets maintained by individual depot supervisors. Executive management cannot determine whether regional fleets are overloaded or idle without manual data consolidation.
* **Evidence**: Management review meetings delayed while awaiting consolidated regional spreadsheets.
* **Traceability**: Addressed via the unified operations dashboard (`/`) displaying real-time metrics across all warehouses, active vehicles, and shipments.

---

### [PA-02] Physical vs. Logged Inventory Discrepancy
* **Problem**: Paper-based and offline spreadsheet inventory tracking leads to drift between recorded counts and actual physical shelf availability.
* **Evidence**: Order fulfillment delays caused when packing staff discovers listed items are missing from warehouse racks.
* **Traceability**: Addressed via `InventoryItem` database records tied directly to `Warehouse` foreign keys, validated through **US-02** and **TC-06**.

---

### [PA-03] Delayed Outbound Stock Decrement
* **Problem**: Stock quantities are updated only at the end of shifts, creating a window where multiple dispatchers allocate the same remaining units to separate shipments.
* **Evidence**: Duplicate order allocations resulting in canceled deliveries and customer complaints.
* **Traceability**: Enforced via **BR-02** (deterministic transactional stock reduction upon dispatch) and verified by **TC-02** (rejection of dispatches exceeding available stock).

---

### [PA-04] Assignment of Inoperable Fleet Vehicles
* **Problem**: Vehicles flagged by mechanics for maintenance are not visibly locked in the dispatch registry, causing dispatchers to assign broken vehicles to time-sensitive routes.
* **Evidence**: Workshop repair cards showing vehicles were scheduled for brake/engine service at the same hour they were assigned to delivery manifests.
* **Traceability**: Enforced via **BR-03** (`Vehicle.clean()` validation rejecting any assignment of vehicles with status `MAINTENANCE`) and verified by **TC-03**.

---

### [PA-05] Tracking Code Collisions and Lost Records
* **Problem**: Manual entry of tracking codes leads to typos, duplicate codes, and customer parcels that cannot be located in the system.
* **Evidence**: Support inquiry records where tracking codes matched multiple consignments or returned zero results.
* **Traceability**: Enforced via **BR-05** (deterministic `LC-TRK-YYYYMMDD-XXXX` pattern with unique database constraint) and verified by **TC-04**.

---

### [PA-06] Transit Overbooking and Passenger Rejection
* **Problem**: Tickets and seat reservations are issued without verifying the physical vehicle's maximum seat capacity, resulting in overbooked coaches and stranded commuters.
* **Evidence**: Passenger grievance filings at central terminals citing sold-out buses with valid pre-purchased receipts.
* **Traceability**: Enforced via **BR-04** ($\text{Remaining Seats} = \text{Capacity} - \text{Bookings}$) and verified by **TC-01** (hard validation failure on booking attempt when remaining seats equal 0).

---

## 4. Requirement Verification Summary

| Pain ID | Business Rule | User Story | Automated Test Case | Test Status in Codebase |
| :---: | :---: | :---: | :---: | :---: |
| **PA-01** | `TR-01` | Dashboard metrics | System check (`manage.py check`) | **Passing** |
| **PA-02** | `BR-02` | `US-02` | `TC-06` (`test_tc06_inventory_quantity_tracking`) | **Passing** |
| **PA-03** | `BR-02` | `US-01` | `TC-02` (Stock validation on dispatch) | **Passing** |
| **PA-04** | `BR-03` | `US-01`, `US-04` | `TC-03` (`test_tc03_reject_vehicle_in_maintenance_on_dispatch`) | **Passing** |
| **PA-05** | `BR-05` | `US-03` | `TC-04` (`test_tc04_public_tracking_view`) | **Passing** |
| **PA-06** | `BR-04` | `US-05` | `TC-01` (`test_tc01_prevent_overbooking_when_capacity_full`) | **Passing** |
