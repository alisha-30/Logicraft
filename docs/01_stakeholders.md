# Key Project Stakeholders

**Project**: LogiCraft: Logistics & Fleet Management  
**Scope**: Fleet tracking, warehouse management, shipment tracking, public-transport scheduling/ticketing  
**Architecture Context**: Python Full-Stack (Django + SQLite) — [PA-01], [N-01]

---

## 1. Executive Summary

This document defines the 4 core stakeholders selected for LogiCraft under **Option A (Lean 4-Stakeholder Scope)**. This set includes **1 key decision-maker**, **2 primary internal operational users**, and **1 primary external public user**, ensuring direct alignment with the dual-domain scope (commercial logistics and municipal public transit).

---

## 2. Core Stakeholders Matrix

| Stakeholder Role | Classification | Primary Responsibility | Current Pain Point | System Benefit & Traceability | Influence Level |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Operations Director** | Decision-Maker | Strategic oversight, fleet allocation, operating budget approval. | Fragmented spreadsheets, delayed reports, lack of centralized operations visibility. | Single-pane real-time dashboard with key metrics for depots, active cargo, and transit load (**TR-01**). | **High** |
| **Fleet Dispatcher** | Primary User (Freight) | Allocates vehicles to shipments, schedules runs, logs route checkpoints. | Risk of double-booking vehicles or dispatching vehicles under repair. | Dropdown filters show only `AVAILABLE` vehicles (**BR-03**); auto-generated tracking IDs (**BR-05**, **US-01**). | **High** |
| **Warehouse Supervisor** | Primary User (Inventory) | Oversees physical storage, logs incoming goods, prepares cargo batches. | Manual stock counts leading to discrepancies and accidental stockouts. | Digital inventory catalog with automatic stock depletion on dispatch (**BR-02**, **US-02**, **TC-02**). | **High** |
| **Public Commuter** | Primary User (Transit) | Plans regional travel, checks bus timetables, reserves passenger seats. | Station overcrowding, uncertainty regarding seat availability. | Direct timetable search and capacity-enforced seat reservations (**BR-04**, **US-05**, **TC-01**). | **Medium** |

---

## 3. Detailed Stakeholder Profiles

### 3.1. Operations Director (Decision-Maker)
* **Profile**: Senior executive responsible for depot efficiency, asset maintenance costs, and commuter service quality.
* **Responsibilities**:
  - Sets company-wide logistics policies and reviews fleet readiness.
  - Approves software systems and workflow standardizations.
* **Pain Points Today**:
  - Relies on daily phone calls and manual end-of-day Excel sheets.
  - Lacks visibility into whether vehicles are idle, in transit, or undergoing maintenance.
* **How LogiCraft Solves This**:
  - Provides an immediate web dashboard displaying live warehouse counts, fleet status ratios, and active shipment volumes (**TR-01**).
* **Decision Authority**: **High** (Final authority on system adoption and operational sign-off).

---

### 3.2. Fleet Dispatcher (Primary Internal User - Freight)
* **Profile**: Front-line logistics coordinator operating out of the central dispatch hub.
* **Responsibilities**:
  - Assigns drivers and vehicles to verified customer orders.
  - Updates cargo checkpoint progress as vehicles advance through waypoints.
* **Pain Points Today**:
  - Accidentally assigning vehicles that are marked for maintenance by mechanics.
  - Generating tracking codes manually, resulting in duplicate or misformatted references.
* **How LogiCraft Solves This**:
  - Enforces **BR-03**: Only vehicles with `status = AVAILABLE` can be assigned during dispatch.
  - Enforces **BR-05**: Auto-generates standardized tracking numbers (`LC-TRK-YYYYMMDD-XXXX`).
  - Implements **US-01** & **TC-03**: Immediate validation feedback during vehicle allocation.
* **Influence Level**: **High** (Core power-user who inputs operational data daily).

---

### 3.3. Warehouse Supervisor (Primary Internal User - Inventory)
* **Profile**: Depot floor manager responsible for stock accuracy and warehouse capacity.
* **Responsibilities**:
  - Logs incoming shipments from manufacturers.
  - Audits warehouse stock levels across SKU categories.
* **Pain Points Today**:
  - Dispatches goods only to find physical inventory is lower than logged count.
  - No automatic synchronization between outbound shipments and warehouse ledger.
* **How LogiCraft Solves This**:
  - Enforces **BR-02**: Outbound shipments decrement stock directly; system prevents negative balances.
  - Implements **US-02** & **TC-06**: Rapid restock updates and per-warehouse inventory filtering.
* **Influence Level**: **High** (Ensures data integrity for the physical supply chain).

---

### 3.4. Public Commuter (Primary External User - Transit)
* **Profile**: Everyday citizen or student utilizing regional transit routes for daily travel.
* **Responsibilities**:
  - Checks route schedules between origin and destination terminals.
  - Books and holds seat reservations.
* **Pain Points Today**:
  - Reaching the bus station only to discover tickets are sold out.
  - No simple, account-free way to verify seat availability online.
* **How LogiCraft Solves This**:
  - Enforces **BR-04** & **TC-01**: Calculates $\text{Remaining Seats} = \text{Capacity} - \text{Confirmed Bookings}$, strictly preventing overbooking.
  - Implements **US-05**: Accessible web timetable with printable booking confirmation slips.
* **Influence Level**: **Medium** (Adoption determines public service success).

---

## 4. Requirements & Traceability Cross-Reference

- **[PA-01]** Phased build supports both freight staff (Dispatcher, Warehouse Supervisor) and transit users (Commuters).
- **[N-01]** Zero-AI rule ensures reliable, transparent calculations that build stakeholder trust without black-box unpredictability.
- **[BR-01 to BR-05]** Business rules directly eliminate the primary friction points identified for each user role.
- **[TC-01 to TC-06]** Verification tests systematically validate stakeholder guarantees (e.g., no overbooking, no negative stock).
