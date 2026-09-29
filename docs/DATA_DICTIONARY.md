# Data Dictionary — AIOps Service Desk

This document provides a comprehensive specification of all relational database tables, columns, constraints, data types, and business purposes in the AIOps Service Desk system.

---

## 1. App: `accounts`

### Table: `accounts_profile`
Stores role-based access control (RBAC) metadata and organizational profile information linked to Django's `auth_user`.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Internal unique profile identifier | Surrogate key |
| `user_id` | ForeignKey (`auth_user`) | OneToOne, Cascade, Unique, Indexed | Reference to Django User account | Maps authentication identity to AIOps persona |
| `role` | CharField(20) | Choices: `EMPLOYEE`, `IT_ADMIN`; Default: `EMPLOYEE` | Access control persona | Enforces portal separation (Employee vs IT Admin) |
| `department` | CharField(100) | Blank allowed, Default: `""` | User's department/division | Departmental reporting and attribution |
| `phone_number` | CharField(20) | Blank allowed, Default: `""` | Contact telephone number | Incident emergency communications |

---

## 2. App: `incidents`

### Table: `incidents_incident`
Core entity representing operational disruptions, service desk tickets, normalized triage state, and lifecycle progression.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate internal key | Primary reference key |
| `incident_number` | CharField(20) | Unique, Indexed, Format: `INC-XXXX` | Human-readable sequential incident identifier | Service desk ticketing tracking |
| `title` | CharField(200) | Max Length: 200, Required | Short incident summary | Brief ticket title |
| `description` | TextField | Required | Detailed raw symptom report submitted by user | Input source for NLP analysis |
| `category` | CharField(20) | Choices: `SERVER`, `DATABASE`, `NETWORK`, `APPLICATION`, `STORAGE`, `SECURITY`, `OTHER` | High-level infrastructure domain | Categorization and filtering |
| `priority` | CharField(20) | Choices: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`; Default: `MEDIUM` | Reported urgency level | Operational prioritization |
| `status` | CharField(25) | Choices: `OPEN`, `ANALYZING`, `RECOMMENDATION_READY`, `PENDING_APPROVAL`, `APPROVED`, `IN_PROGRESS`, `RESOLVED`, `FAILED`, `REJECTED`; Default: `OPEN` | Current lifecycle state | Finite state machine progression |
| `intent` | CharField(50) | Default: `Unknown`, Blank allowed | Normalized problem intent (e.g. `Service Outage`, `Service Degradation`, `Access Issue`) | Deterministic triage classification |
| `service` | CharField(50) | Default: `Unknown`, Blank allowed | Classified infrastructure service (e.g. `Web Server`, `Database`, `Network`) | Targeted runbook filtering |
| `classified_priority`| CharField(10) | Default: `P3`, Blank allowed | Algorithmic triage priority recommendation (`P1`, `P2`, `P3`, `P4`) | Triaged SLA recommendation |
| `normalized_description`| TextField | Blank allowed, Default: `""` | Canonical synthesized problem description | Standardized summary for operators |
| `classification_method`| CharField(80) | Default: `Rule-based local classification` | Triage algorithm identifier | Auditability of AI decision method |
| `created_by_id` | ForeignKey (`auth_user`) | Cascade, Indexed | Submitting user account | Ownership and ticket access control |
| `created_at` | DateTimeField | Auto now add, Indexed | Creation UTC timestamp | SLA calculation and timeline auditing |
| `updated_at` | DateTimeField | Auto now, Indexed | Last update UTC timestamp | State change tracking |
| `resolved_at` | DateTimeField | Nullable, Blank allowed | Resolution UTC timestamp | MTTR calculation and SLA fulfillment |

### Table: `incidents_incidentactivity`
Audit trail of timeline transitions and operator actions for an incident ticket.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `incident_id` | ForeignKey (`incidents_incident`) | Cascade, Indexed | Target incident reference | Relates activity to specific ticket |
| `actor_id` | ForeignKey (`auth_user`) | Nullable, Set Null | User performing the action | Operator attribution |
| `action` | CharField(50) | Required (e.g. `REPORTED`, `AI_ANALYSIS_COMPLETED`, `APPROVAL_REQUESTED`) | Standard action code | Categorized timeline events |
| `description` | TextField | Required | Narrative explanation of event | Human-readable audit log |
| `created_at` | DateTimeField | Auto now add, Indexed | UTC event timestamp | Chronological event ordering |

### Table: `incidents_incidentfeedback`
Continuous improvement telemetry recording employee satisfaction and feedback on resolved runbook procedures.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `incident_id` | OneToOneField (`incidents_incident`) | Cascade, Unique, Indexed | Resolved incident ticket reference | Guarantees one feedback per ticket |
| `user_id` | ForeignKey (`auth_user`) | Cascade, Indexed | Submitting employee reference | Ownership and feedback integrity |
| `rating` | IntegerField | Choices: `1` to `5`, Required | 1 to 5 star satisfaction score | Numerical quality metric |
| `comment` | TextField | Blank allowed | Constructive suggestions / notes | Knowledge base refinement input |
| `created_at` | DateTimeField | Auto now add, Indexed | Submission UTC timestamp | Feedback telemetry timeline |

---

## 3. App: `runbooks`

### Table: `runbooks_runbook`
Operational repository of canonical troubleshooting procedures, indicative symptoms, and automation script bindings.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `runbook_number` | CharField(20) | Unique, Indexed, Format: `RB-XXXX` | Canonical runbook identifier | Standardized procedure indexing |
| `title` | CharField(200) | Required | Runbook procedure title | Searchable catalog name |
| `category` | CharField(20) | Choices matching Incident.Category | Associated domain | Category matching in retrieval |
| `description` | TextField | Required | Summary of problem domain and approach | Corpus text for TF-IDF vectorization |
| `symptoms` | TextField | Required | Multiline indicative error messages | Key symptom matching tokens |
| `steps` | TextField | Required | Ordered step-by-step remediation guide | Standard operating procedure instructions |
| `risk_level` | CharField(20) | Choices: `LOW`, `MEDIUM`, `HIGH`; Default: `MEDIUM` | Operational risk level | Human review scrutiny level |
| `automation_action` | CharField(100) | Blank allowed, Default: `""` | Linked `SAFE_ACTIONS` function identifier | Simulation execution binding |
| `is_active` | BooleanField | Default: `True`, Indexed | Active knowledge base status flag | Prevents retrieval of deprecated procedures |
| `created_by_id` | ForeignKey (`auth_user`) | Cascade | Author user reference | Runbook author attribution |
| `created_at` | DateTimeField | Auto now add | Creation UTC timestamp | Versioning tracking |
| `updated_at` | DateTimeField | Auto now | Last updated UTC timestamp | Modification auditing |

### Table: `runbooks_runbookrecommendation`
Stores the local NLP TF-IDF retrieval result and citation evidence linking an incident to a candidate runbook.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `incident_id` | OneToOneField (`incidents_incident`) | Cascade, Unique, Indexed | Target incident reference | One recommendation per incident |
| `runbook_id` | ForeignKey (`runbooks_runbook`) | Cascade, Indexed | Recommended runbook reference | Recommendation destination |
| `match_score` | FloatField | Range: `0.0` to `1.0`, Required | Cosine similarity match score | Retrieval confidence measurement |
| `citation_metadata` | JSONField | Default: `dict`, Blank allowed | Matched symptoms, steps, category match | Verifiable citation evidence |
| `created_at` | DateTimeField | Auto now add | Analysis UTC timestamp | Timestamp of algorithmic decision |

---

## 4. App: `automation`

### Table: `automation_automationapproval`
Human-in-the-loop review record required before any automated remediation script can be triggered.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `incident_id` | ForeignKey (`incidents_incident`) | Cascade, Indexed | Target incident reference | Links approval to ticket |
| `runbook_id` | ForeignKey (`runbooks_runbook`) | Cascade, Indexed | Approved runbook reference | Specifies approved procedure |
| `requested_by_id`| ForeignKey (`auth_user`) | Cascade | Admin requesting approval | Attribution of approval request |
| `reviewed_by_id` | ForeignKey (`auth_user`) | Nullable, Set Null | Admin granting or rejecting approval | Human-in-the-loop reviewer attribution |
| `status` | CharField(20) | Choices: `PENDING`, `APPROVED`, `REJECTED`; Default: `PENDING` | Approval status state | Strict gate prior to execution |
| `reason` | TextField | Blank allowed | Reviewer notes or mandatory rejection reason | Decision explanation and accountability |
| `created_at` | DateTimeField | Auto now add | Request creation timestamp | Gate request latency tracking |
| `reviewed_at` | DateTimeField | Nullable, Blank allowed | Review completion timestamp | Approval SLA auditing |

### Table: `automation_automationexecution`
Execution record of allowlisted, simulated automation procedures.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `approval_id` | OneToOneField (`automation_automationapproval`)| Cascade, Unique, Indexed | Associated human approval reference | Guarantees 1:1 execution to approval |
| `action_name` | CharField(100) | Required | Identifier of executed allowlisted action | Action traceability |
| `status` | CharField(20) | Choices: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `BLOCKED`; Default: `PENDING` | Current execution status | Execution tracking |
| `output` | TextField | Blank allowed, Default: `""` | Simulated execution output message | Operator log inspection |
| `error_message` | TextField | Blank allowed, Default: `""` | Failure or block reason | Failure diagnosis |
| `started_at` | DateTimeField | Nullable, Blank allowed | Execution start UTC timestamp | Execution timing |
| `completed_at` | DateTimeField | Nullable, Blank allowed | Execution finish UTC timestamp | Duration tracking |

### Table: `automation_verificationresult`
Post-execution health check recording whether problem symptoms were resolved by the automated action.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `execution_id` | OneToOneField (`automation_automationexecution`)| Cascade, Unique, Indexed | Target execution record reference | 1:1 binding to execution |
| `status` | CharField(20) | Choices: `PASSED`, `FAILED` | Verification outcome | Gate for ticket auto-resolution |
| `message` | TextField | Required | Diagnostic verification log message | Confirmation evidence |
| `checked_by_id` | ForeignKey (`auth_user`) | Nullable, Set Null | Operator performing check | Verifier attribution |
| `checked_at` | DateTimeField | Auto now add | Verification UTC timestamp | Verification timeline tracking |

### Table: `automation_auditlog`
Tamper-evident append-only operational log recording every security, AI, and automation event.

| Column Name | Data Type | Constraints | Description | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto Increment | Surrogate key | Primary key |
| `incident_id` | ForeignKey (`incidents_incident`) | Nullable, Cascade, Indexed | Associated incident ticket reference | Contextual event grouping |
| `event_type` | CharField(50) | Indexed (e.g. `AI_ANALYSIS_COMPLETED`, `APPROVAL_REQUESTED`, `AUTOMATION_BLOCKED`) | Canonical event taxonomy | Structured query filtering |
| `message` | TextField | Required | Human-readable event description | Compliance narrative |
| `actor_id` | ForeignKey (`auth_user`) | Nullable, Set Null | User triggering event | Accountability attribution |
| `metadata` | JSONField | Default: `dict`, Blank allowed | Structured operational payloads | Machine-readable forensics |
| `created_at` | DateTimeField | Auto now add, Indexed | Event UTC timestamp | Non-repudiation audit trail |
