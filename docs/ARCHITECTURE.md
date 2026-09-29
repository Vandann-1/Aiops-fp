# System Architecture — AIOps Service Desk

## 1. Executive Architecture Summary

The **AIOps Service Desk with Runbook Retrieval, Safe Automation & Human Approval** is an enterprise-grade service management platform designed for resilient infrastructure operations. The architecture strictly rejects external AI dependencies (such as OpenAI, Gemini, or third-party cloud LLMs) in favor of **deterministic local ticket normalization**, **scikit-learn TF-IDF + Cosine Similarity runbook retrieval**, **verifiable citation evidence**, and **human-in-the-loop gated safe automation simulation**.

```mermaid
flowchart TD
    subgraph UI ["Presentation & Ingestion Layer"]
        EMP["Employee Portal\n(Ticket Submission & Feedback)"]
        ADM["IT Admin Console\n(Triage, Approvals, Runbooks)"]
    end

    subgraph TRIAGE ["Deterministic Normalization Layer"]
        NORM["Rule-Based Classifier\n- Intent (Outage, Degradation, Access, etc.)\n- Service (Web, DB, Network, Storage)\n- Priority (P1, P2, P3, P4)"]
    end

    subgraph NLP ["Local NLP Retrieval Engine"]
        KB["Runbook Knowledge Base\n(12 Canonical Runbooks)"]
        TFIDF["scikit-learn TfidfVectorizer\n& Cosine Similarity Engine"]
        CITE["Citation & Evidence Generator\n(Matched Symptoms & Cited Steps)"]
    end

    subgraph GATE ["Human-in-the-Loop Safety Gate"]
        CHECK["7-Point Diagnostic State Checklist"]
        DRY["Read-Only Dry-Run Preview Engine"]
        REV["Admin Human Approval / Rejection"]
    end

    subgraph EXEC ["Safe Automation Engine"]
        ALLOW["SAFE_ACTIONS Allowlist\n(14 In-Process Simulation Functions)"]
        RUN["Mock Python Executor\n(0 Shell / 0 Subprocesses)"]
    end

    subgraph VERIF ["Verification & Feedback Loop"]
        POST["Post-Execution Health Verification"]
        AUTO_RES["Automated Incident Resolution"]
        FEEDBACK["Operator 1-5 Star Telemetry & Feedback"]
        AUDIT[("Append-Only AuditLog & Activity Stream")]
    end

    EMP -->|Submit Ticket| NORM
    NORM -->|Populate Intent/Service| TFIDF
    KB -->|Corpus Vectorization| TFIDF
    TFIDF -->|Score >= 0.20| CITE
    CITE -->|Recommendation & Evidence| CHECK
    CHECK --> DRY
    DRY --> REV
    REV -->|Approved| ALLOW
    ALLOW --> RUN
    RUN --> POST
    POST -->|Passed| AUTO_RES
    AUTO_RES --> FEEDBACK
    FEEDBACK -->|Procedure Refinement| KB

    NORM -.-> AUDIT
    TFIDF -.-> AUDIT
    REV -.-> AUDIT
    RUN -.-> AUDIT
    POST -.-> AUDIT
```

---

## 2. Core Architectural Components

### 2.1 Web Presentation & Security Boundary
- **Framework**: Django 6.0.7 MVC pattern.
- **Frontend**: Server-rendered HTML templates utilizing Bootstrap 5, Bootstrap Icons, and vanilla JavaScript.
- **Access Control**: Role-Based Access Control (RBAC) separating `EMPLOYEE` and `IT_ADMIN` personas via custom decorators (`@employee_required`, `@it_admin_required`). Object-level ownership prevents employees from viewing or rating tickets belonging to other users.

### 2.2 Deterministic Normalization & Triage Layer (`incidents/normalization.py`)
- Standardizes unstructured, noisy user ticket inputs prior to NLP retrieval.
- Evaluates regex token patterns to extract:
  - **Intent**: `Service Outage`, `Service Degradation`, `Access Issue`, `Database Issue`, `Network Issue`, `Storage Issue`, `Configuration Issue`, or `Unknown`.
  - **Service**: `Web Server`, `Database`, `Network`, `Storage`, `Authentication`, `Application`, or `Unknown`.
  - **Priority**: Algorithmic triage mapping (`P1` to `P4`) based on severity tokens and service criticalities.
- Synthesizes a canonical problem summary to remove conversational fluff and maintain uniform data quality.

### 2.3 Local NLP Runbook Retrieval Engine (`runbooks/retrieval.py`)
- **Technology**: `scikit-learn` `TfidfVectorizer` paired with linear cosine similarity (`cosine_similarity`).
- **Corpus Construction**: Dynamically builds document vectors across active runbooks by concatenating:
  $$\text{Document}_i = \text{Runbook.title} \parallel \text{Runbook.description} \parallel \text{Runbook.symptoms} \parallel \text{Runbook.category}$$
- **Thresholding**: Implements an operational minimum confidence cutoff ($\text{threshold} \ge 0.20$). Queries below this threshold return `None`, preventing low-confidence or hallucinated recommendations.
- **Citation Generation**: Deconstructs matched tokens against indicative runbook symptoms and extracts targeted resolution steps, guaranteeing transparent, explainable recommendations.

### 2.4 Pre-Automation Diagnostic Checklist & Dry-Run Engine (`automation/safety.py`, `actions.py`)
- Evaluates 7 live system safety checks before allowing automation:
  1. Incident has an attached runbook.
  2. Runbook is active in the catalog.
  3. Action identifier exists.
  4. Action is present in `SAFE_ACTIONS` allowlist.
  5. Target incident is currently open / eligible.
  6. Explicit human approval exists.
  7. Action is confirmed simulation-safe.
- Generates a **Dry-Run Simulation Preview** displaying expected output, reversibility status, and rollback instructions without mutating system or database state.

### 2.5 Safe Simulation Automation Engine (`automation/executor.py`, `actions.py`)
- **Strict Allowlist**: Only functions explicitly registered in `SAFE_ACTIONS` dictionary are permitted to run.
- **Simulation Guarantee**: Pure in-process Python callable functions. Completely prohibits `os.system`, `subprocess.Popen`, `shell=True`, `eval`, and `exec`.
- **Idempotency Guard**: Prevents duplicate executions on already succeeded approvals.

### 2.6 Post-Execution Verification Service (`automation/verification.py`)
- Simulates an independent operational health check validating service recovery.
- Upon passing, automatically transitions the incident to `RESOLVED` and populates `resolved_at`.
- Upon failure, leaves the incident open for human engineer takeover.

### 2.7 Continuous Feedback & Audit System (`incidents/models.py`, `automation/audit.py`)
- Captures post-resolution employee satisfaction ratings (1–5 stars) and qualitative feedback.
- Telemetry informs IT Admins on runbook clarity, accuracy, and procedure updates.
- Centralized `AuditLog` records tamper-evident chronological records of all operations.

---

## 3. End-to-End Incident Lifecycle Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Emp as Employee
    actor Adm as IT Admin
    participant Web as Django Web Server
    participant Triage as Normalization Layer
    participant NLP as Local NLP Engine
    participant DB as SQLite DB
    participant Exec as Safe Automation Engine

    Emp->>Web: POST /employee/incidents/create/
    Web->>Triage: normalize_incident_data()
    Triage-->>Web: Intent, Service, Priority, Normalized Text
    Web->>DB: Save Incident (Status: OPEN)
    Web->>NLP: retrieve_best_runbook(incident)
    NLP->>DB: Query active Runbooks
    NLP->>NLP: TF-IDF Vectorization & Cosine Similarity
    NLP->>NLP: generate_citation()
    NLP-->>Web: Recommended Runbook + Match Score + Citations
    Web->>DB: Save RunbookRecommendation
    Web-->>Emp: Incident Created with AI Recommendation

    Adm->>Web: POST /admin-portal/incidents/<id>/request-approval/
    Web->>DB: Create AutomationApproval (Status: PENDING)
    Web->>DB: Update Incident Status (PENDING_APPROVAL)
    
    Adm->>Web: GET /admin-portal/approvals/<id>/dry-run/
    Web->>Exec: get_dry_run_preview(action_name)
    Web-->>Adm: Display 7-Point Checklist & Dry-Run Preview
    
    Adm->>Web: POST /admin-portal/approvals/<id>/approve/
    Web->>DB: Update Approval (Status: APPROVED)
    
    Adm->>Web: POST /admin-portal/approvals/<id>/execute/
    Web->>Exec: execute_approved_action()
    Exec->>Exec: Validate Allowlist & Preconditions
    Exec->>Exec: Run In-Process Python Mock Action
    Exec->>DB: Save AutomationExecution (Status: SUCCESS)
    
    Adm->>Web: POST /admin-portal/executions/<id>/verify/
    Web->>Exec: verify_execution()
    Exec-->>Web: Verification PASSED
    Web->>DB: Save VerificationResult
    Web->>DB: Update Incident (Status: RESOLVED)
    
    Emp->>Web: POST /employee/incidents/<id>/feedback/
    Web->>DB: Save IncidentFeedback (Rating, Comment)
```

---

## 4. Key Architectural Decisions & Tradeoffs

| Architecture Decision | Chosen Approach | Rationale | Alternatives Rejected |
| :--- | :--- | :--- | :--- |
| **AI Retrieval Mechanism** | Local TF-IDF + Cosine Similarity (`scikit-learn`) | Zero external network calls, zero API token costs, air-gap compatible, deterministic scoring, fast sub-millisecond execution. | External LLM APIs (OpenAI, Gemini), cloud vector databases (Pinecone). |
| **Automation Strategy** | Pure Python In-Process Simulation | 100% safe for educational capstone review, eliminating accidental system damage, host compromise, or command injection vulnerabilities. | Real OS subprocesses (`bash`, `cmd.exe`), remote SSH agents, SaltStack/Ansible daemons. |
| **Ticket Triage** | Deterministic Regex & Keyword Rule Engine | Explainable, easily testable, highly reproducible, with zero hallucinations and fallback to `Unknown`. | Black-box deep learning classifiers, cloud prompt-based classification. |
| **Database Architecture** | SQLite for development & testing; PostgreSQL schema compatible | Self-contained, portable, zero-setup evaluation harness without external service dependencies. | Requiring live PostgreSQL/pgvector cluster for simple local run. |
| **Human Oversight** | Mandatory Human-in-the-Loop Review Gate | Regulatory compliance, preventing autonomous execution of risky procedures without engineer verification. | Autonomous unattended auto-execution. |
