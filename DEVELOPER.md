# DEVELOPER.md: LogiCraft Project Master Reference

This document serves as the primary technical specification and developer reference for the developer working on **LogiCraft: Logistics & Fleet Management**. It synthesizes the project context, technical stack, directory structure, coding conventions, testing protocols, and Definition of Done based on the complete documentation suite in `docs/`.

---

## 1. Project Context & Non-Negotiable Rules

* **Project**: LogiCraft — Logistics & Fleet Management (Fleet tracking, warehouse management, shipment tracking, public-transport scheduling & ticketing).
* **Ownership & Scope**: Individual Major Project (Full-Stack Solo Developer).
* **Architecture Standard**: All operations, state transitions, allocations, and validations are built using **robust, enterprise-grade Python and Django ORM logic** with strict relational integrity.
* **Traceability Prefix Standards**:
  - `PA-xx`: Problem / Pain Area ([docs/02_pain_areas.md](docs/02_pain_areas.md))
  - `N-xx`: Stakeholder Need ([docs/03_needs.md](docs/03_needs.md))
  - `BR-xx`: Business Requirement ([docs/04_requirements.md](docs/04_requirements.md))
  - `TR-xx`: Technical Requirement ([docs/04_requirements.md](docs/04_requirements.md))
  - `US-xx`: Agile User Story ([docs/06_user_stories.md](docs/06_user_stories.md))
  - `TC-xx`: Test Case ([docs/07_test_cases.md](docs/07_test_cases.md))

---

## 2. Technology Stack (Option 1: Django Monolith)

* **Backend Framework**: Python 3.10+ / Django `5.0.x`
* **Database**: SQLite3 (`db.sqlite3`) with enforced Foreign Key integrity
* **Frontend**: Django Template Language (DTL) + Bootstrap `5.3.3` + Vanilla JavaScript (Zero Node.js build steps)
* **Data Processing**: `pandas`, `numpy`, `Faker` (Fixed seed: `42`)
* **Test Runner**: Django `TestCase` (`unittest`) / `pytest`
* **Environment**: Local virtual environment (`.venv`) managed via `requirements.txt`

---

## 3. Repository & Directory Structure

```text
logicraft/
├── .env.example             # Template for local environment variables
├── .gitignore               # Ignores .venv, __pycache__, db.sqlite3, data CSVs
├── DEVELOPER.md             # Master developer conventions & instruction reference
├── README.md                # Project overview, quickstart, and execution guide
├── manage.py                # Django CLI management entry point
├── requirements.txt         # Pinned runtime dependencies
├── config/                  # Django root project configuration
│   ├── settings.py          # INSTALLED_APPS, templates, static config
│   ├── urls.py              # Root URL router (logistics, transit, admin)
│   └── wsgi.py
├── logistics/               # Core Freight & Fleet Domain App
│   ├── models.py            # Warehouse, InventoryItem, Vehicle, Shipment, Checkpoint
│   ├── forms.py             # ShipmentDispatchForm with atomic inventory validation
│   ├── views.py             # Dashboard, dispatch form, public tracking, auth
│   ├── urls.py              # URL routes for logistics & auth
│   ├── admin.py             # Customized Django admin with inlines and filters
│   ├── tests.py             # TC-03, TC-04, TC-06 automated test cases
│   └── management/commands/ # seed_data.py & load_csv_data.py commands
├── transit/                 # Public Passenger Transit Domain App
│   ├── models.py            # TransitRoute, TransitSchedule, TicketBooking
│   ├── views.py             # Schedules timetable and seat booking views
│   ├── urls.py              # URL routes for transit
│   ├── admin.py             # Customized admin for schedules & bookings
│   └── tests.py             # TC-01 capacity limit test cases
├── templates/               # Server-rendered HTML templates
│   ├── base.html            # Bootstrap 5 layout, navbar, session alerts, footer
│   ├── home.html            # Operations dashboard with metric cards & charts (BR-01)
│   ├── accounts/            # Staff portal authentication (login.html, register.html)
│   ├── logistics/           # Cargo dispatch (dispatch_form.html) & tracking (track_shipment.html)
│   └── transit/             # Timetable, booking, and ticket receipt templates
├── static/                  # Static assets (custom CSS/JS)
├── data/                    # Generated synthetic CSV datasets (8 CSV files)
├── src/                     # Data engineering & utility scripts
│   └── generate_data.py     # Reproducible synthetic dataset generator (Seed=42)
├── tests/                   # Root integration & system smoke tests
│   ├── __init__.py
│   ├── test_system.py       # Cross-app endpoint smoke tests & staff auth tests
│   ├── test_dispatch_form.py # Atomic inventory deduction & vehicle lockout tests
│   └── test_journeys.py     # End-to-end multi-step user journey & failure resiliency tests
└── docs/                    # Complete Software Engineering documentation suite (01 to 10)
    ├── 01_stakeholders.md   # 4 core stakeholders and decision authority
    ├── 02_pain_areas.md     # 6 shortlisted operational pain areas (PA-01 to PA-06)
    ├── 03_needs.md          # Needs analysis & HMW questions (N-01 to N-06)
    ├── 04_requirements.md   # Formal BR and TR requirements (BR-01 to BR-09)
    ├── 05_traceability.md   # Traceability matrix, MVP scope, and prioritisation
    ├── 06_user_stories.md   # Agile user stories with acceptance criteria
    ├── 07_test_cases.md     # Comprehensive test matrix (Happy/Invalid/Edge)
    ├── 08_architecture_tech_stack.md # Technology stack architecture & module engineering domains
    ├── 09_data_design.md    # Database schema, ER diagram, data dictionary & edge cases
    ├── 10_backend_integration.md # Master interface-to-backend operations mapping
    └── wireframe.html       # Self-contained grayscale interactive prototype
```

---

## 4. Coding & Architectural Conventions

1. **Python / Django Conventions**:
   * Adhere strictly to **PEP 8** style guidelines.
   * Model fields must always define explicit `help_text` and relevant constraints (`unique=True`, `max_length`, `choices`).
   * Choices must be defined as uppercase model constants:
     ```python
     STATUS_AVAILABLE = 'AVAILABLE'
     STATUS_CHOICES = [(STATUS_AVAILABLE, 'Available'), ...]
     ```
   * Enforce business logic inside `Model.clean()` methods rather than scattered across views:
     * **BR-02 / BR-03**: Stock must decrement upon dispatch; negative balances strictly prohibited.
     * **BR-04**: Maintenance vehicles locked from shipment assignments.
     * **BR-06**: Confirmed bookings cannot exceed `vehicle.capacity`.
2. **Frontend Conventions**:
   * Grayscale or clean standard Bootstrap 5 styling.
   * Server-side rendering using Django Template Language (DTL).
   * No heavy front-end build dependencies (No Node/npm, Webpack, React, or Vue).
3. **Data & Privacy Conventions**:
   * **BR-08**: 100% of test user and passenger email addresses must use the reserved RFC domain `@example.com`. No real personal names or phone numbers.
   * Dataset generation must use `random_seed = 42` for strict reproducibility.

---

## 5. Standard CLI Execution Commands

Execute all commands from the project root (`logicraft/`):

```powershell
# 1. Activate Environment & Run Development Server
.\.venv\Scripts\python.exe manage.py runserver

# 2. Run All 33 Automated Unit, Integration & Journey Tests
.\.venv\Scripts\python.exe manage.py test logistics transit tests -v 2

# 3. Verify Django System Health & Configuration
.\.venv\Scripts\python.exe manage.py check

# 4. Generate Synthetic Datasets (data/*.csv)
.\.venv\Scripts\python.exe src/generate_data.py

# 5. Ingest Synthetic CSV Datasets into SQLite Database
.\.venv\Scripts\python.exe manage.py load_csv_data

# 6. Populate SQLite Database with Realistic Demo Data
.\.venv\Scripts\python.exe manage.py seed_data

# 7. Apply Schema Migrations
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

---

## 6. Definition of Done (DoD)

A user story, bug fix, or feature is considered **Done** only when all of the following criteria are satisfied:

1. **Functional Correctness**:
   - Implements the exact behavior described in the linked User Story (`US-xx`) and Business Requirement (`BR-xx`).
   - Satisfies all Given/When/Then acceptance criteria.
2. **Code Quality & Constraint Verification**:
   - Follows clean code standards, PEP 8, and strict schema validations.
3. **Automated Testing**:
   - Corresponding test case added or passing in `logistics/tests.py`, `transit/tests.py`, or `tests/test_system.py`.
   - `python manage.py test` executes with **100% pass rate (0 errors, 0 failures)**.
4. **Data Integrity & Privacy**:
   - `python manage.py check` returns `0 issues`.
   - Seed scripts and test fixtures contain **zero real personal data** (all emails end with `@example.com`).
5. **Documentation Synchronized**:
   - Any added or modified model field is updated in [docs/09_data_design.md](docs/09_data_design.md).
