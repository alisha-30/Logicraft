# LogiCraft: Agile User Stories & Acceptance Criteria

**Document Reference**: `docs/06_user_stories.md`  
**Traceability Reference**: [docs/05_traceability.md](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/docs/05_traceability.md)  
**Requirements Source**: [docs/04_requirements.md](file:///C:/Users/KAIN/OneDrive/Desktop/logicraft/docs/04_requirements.md)  
**Project Scope**: Enterprise Full-Stack Application | Author / Scope: Solo Developer (Individual Project)

---

## 1. Executive Summary

This document specifies the complete user story catalog for LogiCraft. Every user story adheres to strict software engineering standards:
1. Written strictly from a **user/stakeholder perspective** (`As a <role> I want <action> so that <benefit>`). Zero technical stories (e.g., no stories like "I want a database").
2. Each story includes **2 to 3 testable Given/When/Then acceptance criteria**.
3. Every story is mapped directly to its **Business Requirement ID (BR)**.
4. Sized with realistic student effort estimates of **1 to 3 days** (no oversized epics).

---

## 2. Core Functional User Stories

### [US-01] Operations Performance Dashboard
* **Linked Requirement**: `BR-01`
* **Scope & Priority**: **MVP (Report)** | **Must Have**
* **Effort Estimate**: 2 Days
* **User Story**:  
  > **As an** Operations Director,  
  > **I want to** view a centralized operations dashboard displaying live summary counts of warehouses, available fleet vehicles, and active shipments,  
  > **so that** I can assess regional logistics throughput without waiting for delayed end-of-day email spreadsheets.

#### Acceptance Criteria
* **AC-1.1**:
  * **Given** registered warehouses, fleet vehicles, and active shipments exist in the database,
  * **When** the Operations Director loads the dashboard page (`/`),
  * **Then** the metric cards must display integer values identical to the database row counts.
* **AC-1.2**:
  * **Given** a shipment is transitioned to `Delivered` or a new shipment is created,
  * **When** the Operations Director refreshes the dashboard,
  * **Then** the "Active Shipments" counter must immediately reflect the updated total.

---

### [US-02] Warehouse Inventory Cataloging
* **Linked Requirement**: `BR-02`
* **Scope & Priority**: **MVP (Data)** | **Must Have**
* **Effort Estimate**: 1 Day
* **User Story**:  
  > **As a** Warehouse Supervisor,  
  > **I want to** catalog inventory items bound to a specific warehouse facility,  
  > **so that** our depot staff knows the exact storage location and quantity on hand for every SKU.

#### Acceptance Criteria
* **AC-2.1**:
  * **Given** a supervisor creates a new item with SKU, name, category, and an assigned warehouse,
  * **When** the supervisor saves the form,
  * **Then** the item is stored in the database with a valid warehouse link and appears in that warehouse's stock list.
* **AC-2.2**:
  * **Given** a supervisor attempts to save an item without selecting a warehouse,
  * **When** the form submission is processed,
  * **Then** the system must reject the save and display a validation error requiring a warehouse selection.

---

### [US-03] Immediate Outbound Stock Decrement
* **Linked Requirement**: `BR-03`
* **Scope & Priority**: **MVP (Logic)** | **Must Have**
* **Effort Estimate**: 2 Days
* **User Story**:  
  > **As a** Warehouse Supervisor,  
  > **I want** warehouse stock counts to automatically decrease when a shipment is dispatched,  
  > **so that** available inventory records prevent warehouse staff from promising the same physical goods to multiple orders.

#### Acceptance Criteria
* **AC-3.1**:
  * **Given** an inventory item with quantity 20 at a warehouse,
  * **When** a dispatcher confirms a shipment of 5 units of that item with status `Dispatched`,
  * **Then** the item's stored stock quantity must immediately reduce to 15.
* **AC-3.2**:
  * **Given** an inventory item with quantity 3 on hand,
  * **When** a user attempts to dispatch an order requesting 5 units,
  * **Then** the system must reject the dispatch transition with a stock-deficit error and retain the stock count at 3.

---

### [US-04] Inoperable Fleet Vehicle Lockout
* **Linked Requirement**: `BR-04`
* **Scope & Priority**: **Final (Stretch)** | **Should Have**
* **Effort Estimate**: 1 Day
* **User Story**:  
  > **As a** Fleet Dispatcher,  
  > **I want** vehicles undergoing maintenance to be blocked from trip assignment,  
  > **so that** drivers are never dispatched in unroadworthy or servicing vehicles.

#### Acceptance Criteria
* **AC-4.1**:
  * **Given** a vehicle has its status set to `Under Maintenance`,
  * **When** a dispatcher selects that vehicle for an active shipment dispatch,
  * **Then** the system must raise a validation error stating the vehicle cannot be assigned while under repair.
* **AC-4.2**:
  * **Given** a vehicle's maintenance is completed and status is updated to `Available`,
  * **When** a dispatcher assigns that vehicle to a new shipment,
  * **Then** the system must successfully accept and save the assignment.

---

### [US-05] Public Cargo Tracking & Audit History
* **Linked Requirement**: `BR-05`
* **Scope & Priority**: **MVP (Screen)** | **Must Have**
* **Effort Estimate**: 2 Days
* **User Story**:  
  > **As a** Cargo Customer,  
  > **I want to** enter my tracking code on the public website without logging in,  
  > **so that** I can view the chronological transit progress and current status of my package.

#### Acceptance Criteria
* **AC-5.1**:
  * **Given** a valid tracking number matching `LC-TRK-YYYYMMDD-XXXX`,
  * **When** the customer submits the code on the public tracking search bar,
  * **Then** the system renders a milestone stepper and chronological checkpoint audit timeline with HTTP status 200.
* **AC-5.2**:
  * **Given** a customer enters a non-existent tracking code,
  * **When** the search is executed,
  * **Then** the system renders a clean "Tracking Number Not Found" notice without throwing an unhandled exception.

---

### [US-06] Capacity-Constrained Public Transit Booking
* **Linked Requirement**: `BR-06`
* **Scope & Priority**: **Final (Stretch)** | **Could Have**
* **Effort Estimate**: 2 Days
* **User Story**:  
  > **As a** Public Commuter,  
  > **I want to** search bus route timetables and reserve an available seat in advance,  
  > **so that** my seat is guaranteed upon boarding and I am never turned away due to bus overcrowding.

#### Acceptance Criteria
* **AC-6.1**:
  * **Given** a scheduled bus trip with remaining seats greater than 0,
  * **When** a commuter enters their passenger name, email, and seat number,
  * **Then** the system confirms the booking, issues a unique booking reference, and decrements the remaining seat counter by 1.
* **AC-6.2**:
  * **Given** a scheduled bus trip where confirmed bookings equal the bus seating capacity,
  * **When** a commuter attempts to reserve a seat,
  * **Then** the system disables the booking action or returns a "Route fully booked" error without creating a booking record.

---

## 3. Standing Cross-Cutting User Stories

### [US-07] Non-Negative Ledger Integrity
* **Linked Requirement**: `BR-07`
* **Scope & Priority**: **MVP (Foundational)** | **Must Have**
* **Effort Estimate**: 1 Day
* **User Story**:  
  > **As a** Warehouse Supervisor,  
  > **I want** the system to enforce strict positive numbers for inventory quantities and vehicle capacities,  
  > **so that** accidental negative numbers can never corrupt warehouse ledgers or fleet records.

#### Acceptance Criteria
* **AC-7.1**:
  * **Given** an inventory creation or vehicle registration form,
  * **When** a user enters a negative integer (e.g., `-5`),
  * **Then** the system rejects the input with an explicit field validation error.

---

### [US-08] Synthetic Data Privacy Protection
* **Linked Requirement**: `BR-08`
* **Scope & Priority**: **MVP (Foundational)** | **Must Have**
* **Effort Estimate**: 1 Day
* **User Story**:  
  > **As an** Academic Evaluator,  
  > **I want** all pre-seeded demonstration data to use fictitious names, addresses, and test email domains,  
  > **so that** no real personal identifiable information (PII) is exposed during project evaluation.

#### Acceptance Criteria
* **AC-8.1**:
  * **Given** the initial database seeding script (`python manage.py seed_data`),
  * **When** the demo data is inspected,
  * **Then** 100% of seeded email records must use the reserved RFC test domain `@example.com`.

---

### [US-09] Pinned Reproducibility Manifest
* **Linked Requirement**: `BR-09`
* **Scope & Priority**: **MVP (Foundational)** | **Must Have**
* **Effort Estimate**: 1 Day
* **User Story**:  
  > **As a** Student Evaluator,  
  > **I want** all Python dependencies pinned in a `requirements.txt` file,  
  > **so that** I can clone and execute the project locally in an isolated virtual environment without version conflict errors.

#### Acceptance Criteria
* **AC-9.1**:
  * **Given** a standard Python 3.10+ virtual environment,
  * **When** the user runs `pip install -r requirements.txt`,
  * **Then** all required packages install successfully with exit code 0.

---

## 4. Effort Estimation & Sprint Schedule Summary

| Story ID | Role | Requirement | MoSCoW Priority | Scope | Estimated Effort |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **US-01** | Operations Director | `BR-01` | **Must Have** | **MVP (Report)** | 2 Days |
| **US-02** | Warehouse Supervisor | `BR-02` | **Must Have** | **MVP (Data)** | 1 Day |
| **US-03** | Warehouse Supervisor | `BR-03` | **Must Have** | **MVP (Logic)** | 2 Days |
| **US-05** | Cargo Customer | `BR-05` | **Must Have** | **MVP (Screen)** | 2 Days |
| **US-07** | Warehouse Supervisor | `BR-07` | **Must Have** | **MVP (Foundational)** | 1 Day |
| **US-08** | Academic Evaluator | `BR-08` | **Must Have** | **MVP (Foundational)** | 1 Day |
| **US-09** | Student Evaluator | `BR-09` | **Must Have** | **MVP (Foundational)** | 1 Day |
| **US-04** | Fleet Dispatcher | `BR-04` | **Should Have** | **Final (Stretch)** | 1 Day |
| **US-06** | Public Commuter | `BR-06` | **Could Have** | **Final (Stretch)** | 2 Days |

*Total MVP Effort*: **10 Days** (Perfect fit for the 10-day build sprint).  
*Total Stretch Effort*: **3 Days** (Executed in Phase 2 / Final polish).
