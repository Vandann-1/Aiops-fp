# API Contracts & Endpoint Specification — AIOps Service Desk

This document defines the complete interface contract for all endpoints across the AIOps Service Desk platform.

---

## 1. Authentication & Profile Endpoints (`accounts`)

### `GET|POST /login/`
- **Description**: Authenticates users and redirects to persona-specific dashboards.
- **HTTP Methods**: `GET` (renders login form), `POST` (submits credentials).
- **Request Payload** (`POST`):
  - `username` (string, required)
  - `password` (string, required)
- **Response**:
  - `GET`: HTML page (HTTP 200).
  - `POST` Success: HTTP 302 redirect to `/admin-portal/dashboard/` for IT Admins or `/employee/dashboard/` for Employees.
  - `POST` Invalid: HTML page with error message (HTTP 200).
- **Auth Required**: No.
- **Role Required**: None.

### `POST /logout/`
- **Description**: Terminates active session and invalidates authentication tokens.
- **HTTP Methods**: `POST`.
- **Response**: HTTP 302 redirect to `/login/`.
- **Auth Required**: Yes.
- **Role Required**: None.

### `GET /employee/profile/`
- **Description**: Displays current employee user information and ticket statistics.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `EMPLOYEE` (IT Admin redirected to `/admin-portal/dashboard/`).

### `GET /admin-portal/profile/`
- **Description**: Displays IT Admin profile and system permissions overview.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

---

## 2. Employee Incident Endpoints (`incidents`)

### `GET /employee/dashboard/`
- **Description**: Employee workspace displaying personal incident counters and recent activity.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `EMPLOYEE`.

### `GET /employee/incidents/`
- **Description**: Paginated list of incidents submitted by the authenticated employee.
- **HTTP Methods**: `GET`.
- **Query Parameters**:
  - `page` (integer, optional, default: 1)
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `EMPLOYEE`.

### `GET|POST /employee/incidents/create/`
- **Description**: Ingests, deterministically normalizes, and triggers local AI runbook retrieval for new incidents.
- **HTTP Methods**: `GET` (renders form), `POST` (submits new ticket).
- **Request Payload** (`POST`):
  - `title` (string, required, max 200 chars)
  - `description` (string, required)
  - `category` (string, choices: `SERVER`, `DATABASE`, `NETWORK`, `APPLICATION`, `STORAGE`, `SECURITY`, `OTHER`)
  - `priority` (string, choices: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- **Response**:
  - `GET`: HTML page (HTTP 200).
  - `POST` Success: HTTP 302 redirect to `/employee/incidents/<pk>/`.
  - `POST` Invalid: HTML page with validation errors (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `EMPLOYEE`.

### `GET /employee/incidents/<int:pk>/`
- **Description**: Ticket detail view enforcing object-level ownership check.
- **HTTP Methods**: `GET`.
- **Path Parameters**: `pk` (incident primary key).
- **Response**: HTML page (HTTP 200) or HTTP 404 if not found / belonging to another user.
- **Auth Required**: Yes.
- **Role Required**: `EMPLOYEE`.

### `POST /employee/incidents/<int:pk>/feedback/`
- **Description**: Submits post-resolution satisfaction rating and procedure comments.
- **HTTP Methods**: `POST`.
- **Path Parameters**: `pk` (incident primary key).
- **Request Payload**:
  - `rating` (integer, required, 1 to 5)
  - `comment` (string, optional)
- **Response**: HTTP 302 redirect to `/employee/incidents/<pk>/`. Rejects duplicate feedback.
- **Auth Required**: Yes.
- **Role Required**: `EMPLOYEE` (must own the incident; incident status must be `RESOLVED`).

---

## 3. IT Admin Incident & Overview Endpoints (`incidents`)

### `GET /admin-portal/dashboard/`
- **Description**: Master operations console displaying live incident queues, open approvals, and recent audit activity.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/project-overview/` (or `/admin-portal/overview/`)
- **Description**: Capstone overview console with system architecture, safety controls, and benchmark evaluation figures.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/incidents/`
- **Description**: Filterable and searchable queue of all incidents across the organization.
- **HTTP Methods**: `GET`.
- **Query Parameters**:
  - `search` / `q` (string, optional)
  - `status` (string, optional)
  - `priority` (string, optional)
  - `category` (string, optional)
  - `page` (integer, optional)
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/incidents/critical/`
- **Description**: Filtered view displaying only `HIGH` and `CRITICAL` open incidents.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/incidents/<int:pk>/`
- **Description**: Comprehensive admin ticket inspection with triage details, citation evidence, diagnostic checklist, and dry-run preview.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200) or HTTP 404.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/incidents/<int:pk>/update/`
- **Description**: Modifies ticket status or priority manually.
- **HTTP Methods**: `POST`.
- **Request Payload**:
  - `status` (string, choices matching `Incident.Status`)
  - `priority` (string, choices matching `Incident.Priority`)
- **Response**: HTTP 302 redirect to incident detail.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/incidents/<int:pk>/analyze/`
- **Description**: Triggers on-demand re-execution of the local NLP TF-IDF retrieval engine.
- **HTTP Methods**: `POST`.
- **Response**: HTTP 302 redirect to incident detail with updated recommendation and citation metadata.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

---

## 4. Runbook Knowledge Base Endpoints (`runbooks`)

### `GET /admin-portal/runbooks/`
- **Description**: Searchable catalog of standard operating procedures.
- **HTTP Methods**: `GET`.
- **Query Parameters**: `search`, `category`, `risk`, `active`, `page`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET|POST /admin-portal/runbooks/create/`
- **Description**: Authors a new runbook procedure with indicative symptoms and script hook bindings.
- **HTTP Methods**: `GET`, `POST`.
- **Response**: `GET`: HTML form (HTTP 200); `POST`: HTTP 302 redirect to runbook detail.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/runbooks/<int:pk>/`
- **Description**: Displays full runbook text, symptoms, steps, linked automation action, and operator feedback history.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200) or HTTP 404.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET|POST /admin-portal/runbooks/<int:pk>/edit/`
- **Description**: Edits runbook resolution procedure or symptoms to incorporate operational feedback.
- **HTTP Methods**: `GET`, `POST`.
- **Response**: `GET`: HTML form (HTTP 200); `POST`: HTTP 302 redirect to runbook detail.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/runbooks/<int:pk>/toggle-active/`
- **Description**: Soft activates or deactivates a runbook. Inactive runbooks are excluded from AI retrieval.
- **HTTP Methods**: `POST`.
- **Response**: HTTP 302 redirect to runbook detail.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/runbooks/feedback/`
- **Description**: Continuous improvement console aggregating employee ratings and feedback across all runbooks.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

---

## 5. Human Approval & Safe Automation Endpoints (`automation`)

### `POST /admin-portal/incidents/<int:pk>/request-approval/`
- **Description**: Creates a pending human review gate for an incident's recommended runbook.
- **HTTP Methods**: `POST`.
- **Response**: HTTP 302 redirect to approval review page. Rejects if no active recommendation exists.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/approvals/`
- **Description**: Queue of pending, approved, and rejected automation approval requests.
- **HTTP Methods**: `GET`.
- **Query Parameters**: `status` (choices: `PENDING`, `APPROVED`, `REJECTED`, `ALL`).
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/approvals/<int:pk>/`
- **Description**: Human-in-the-loop review interface with 7-point diagnostic safety checklist and dry-run preview.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200) or HTTP 404.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/approvals/<int:pk>/dry-run/`
- **Description**: Dedicated dry-run inspection page simulating execution without modifying database or system state.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200) or HTTP 404.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/approvals/<int:pk>/approve/`
- **Description**: Records human approval for automated execution. Does not execute the action.
- **HTTP Methods**: `POST`.
- **Request Payload**: `reason` (string, optional notes).
- **Response**: HTTP 302 redirect. Rejects already approved/rejected requests.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/approvals/<int:pk>/reject/`
- **Description**: Rejects automation recommendation with mandatory justification.
- **HTTP Methods**: `POST`.
- **Request Payload**: `reason` (string, required).
- **Response**: HTTP 302 redirect. Rejects already approved/rejected requests.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/approvals/<int:pk>/execute/`
- **Description**: Triggers safe simulation execution for an approved action. Validates allowlist and idempotency.
- **HTTP Methods**: `POST`.
- **Response**: HTTP 302 redirect. Blocks unapproved, rejected, or unallowlisted actions with an `AuditLog` entry.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/executions/<int:pk>/`
- **Description**: Detailed telemetry and console output from a simulated automation run.
- **HTTP Methods**: `GET`.
- **Response**: HTML page (HTTP 200) or HTTP 404.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `POST /admin-portal/executions/<int:pk>/verify/`
- **Description**: Runs simulated post-execution health check. Auto-resolves ticket if passed.
- **HTTP Methods**: `POST`.
- **Response**: HTTP 302 redirect.
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.

### `GET /admin-portal/audit-logs/`
- **Description**: Searchable chronological view of all security, triage, approval, and execution audit records.
- **HTTP Methods**: `GET`.
- **Query Parameters**: `event_type`, `incident`, `actor`, `page`.
- **Response**: HTML page (HTTP 200).
- **Auth Required**: Yes.
- **Role Required**: `IT_ADMIN`.
