# College Capstone Viva Demonstration Script

**Project Title**: AIOps Service Desk with Runbook Retrieval, Safe Automation & Human Approval  
**Presentation Time**: 8–10 Minutes  
**Target Audience**: Academic Reviewers, External Examiners, Senior Engineering Evaluators  

---

## Pre-Demo Setup & Credentials

Before beginning the viva demonstration, launch the local server in your terminal:
```bash
# Terminal 1: Launch Django Server
.\venv\Scripts\python.exe manage.py runserver
```

**Pre-seeded Demonstration Credentials**:
- **IT Administrator**: `admin` / `admin1234`
- **Employee User**: `employeee` / `employeee1234`

Open your web browser to `http://127.0.0.1:8000/`.

---

## Scene 1: The Problem & Architecture Overview (1.5 Minutes)

1. **Log in as IT Admin**:
   - URL: `http://127.0.0.1:8000/login/`
   - Enter `admin` / `admin1234`.
2. **Navigate to the Capstone Overview Console**:
   - Click **Capstone Overview** in the left sidebar (or visit `http://127.0.0.1:8000/admin-portal/project-overview/`).
3. **Presenter Talking Points**:
   > *"Good morning, esteemed committee members. In modern cloud operations, incident triage and runbook lookup are often slow and error-prone, while fully autonomous AI automation is unacceptably dangerous.  
   > Our project solves this through a controlled AIOps architecture with three foundational pillars:  
   > 1. **100% Local NLP**: Zero external AI APIs, zero token costs, and zero data leakage. We use scikit-learn TF-IDF with Cosine Similarity and verifiable citation metadata.  
   > 2. **Deterministic Triage**: Rule-based normalization that accurately extracts Intent, Service, and Priority without LLM hallucinations.  
   > 3. **Human-in-the-Loop Safety Gates**: Pre-execution 7-point diagnostic checklists, read-only dry-runs, and safe simulation execution with zero OS subprocesses."*

---

## Scene 2: Ticket Ingestion & Deterministic Triage (1.5 Minutes)

1. **Switch to Employee Persona**:
   - Click **Logout** at the bottom of the sidebar.
   - Log in as `employeee` / `employeee1234`.
2. **Submit a Realistic Incident**:
   - Click **Report Incident** in the sidebar.
   - Enter the following details:
     - **Title**: `Production Web Server returning 502 Bad Gateway`
     - **Category**: `Server`
     - **Priority**: `High`
     - **Description**: `Users are unable to access the web portal. Nginx service appears unresponsive and connection is refused after the latest deployment.`
   - Click **Submit Incident**.
3. **Highlight the Live Normalization**:
   - Point out the **AI-Assisted Classification** card:
     - **Intent**: `Service Outage`
     - **Service**: `Web Server`
     - **Suggested Priority**: `P1`
     - **Method**: `Rule-based local classification`
   > *"Notice that as soon as the ticket is ingested, our deterministic triage layer immediately extracted structured metadata and normalized the problem text without calling external APIs."*

---

## Scene 3: Explainable Retrieval & Runbook Citations (1.5 Minutes)

1. **Inspect AI Recommendation**:
   - On the same incident detail page, scroll to the **Recommended Runbook** card:
     - **Runbook**: `RB-0001 — Restart Nginx Web Server`
     - **Match Score**: High similarity confidence ($\approx 65\% - 75\%$).
2. **Demonstrate Verifiable Citations**:
   - Point to the **Runbook Citations & Evidence** box:
     - **Matched Symptoms**: `Nginx service inactive`, `HTTP 502/503 errors`, `Connection refused`.
     - **Cited Action Steps**: Displays the exact procedure steps from the canonical runbook.
   > *"Unlike black-box models, our local NLP engine provides verifiable evidence. It cites the exact matching symptoms and resolution steps that justified this recommendation."*

---

## Scene 4: Pre-Automation Safety & Dry-Run Preview (1.5 Minutes)

1. **Log back in as IT Admin**:
   - Logout and log in as `admin` / `admin1234`.
2. **Open the Incident Ticket**:
   - Go to **All Incidents** and click the new ticket `INC-0004`.
3. **Request Automation Approval**:
   - In the right-hand panel, click **Request Approval**.
   - You will be redirected to the **Human Review Panel** (`/admin-portal/approvals/<id>/`).
4. **Inspect Safety Gates**:
   - **Diagnostic Checklist**: Highlight that all 7 live system checks are verified (runbook active, action allowlisted, incident open).
   - **Dry-Run Preview**: Click **Open Full Dry-Run Inspection**.
   > *"Before an engineer approves anything, they inspect a read-only dry-run preview. It states the expected outcome, confirms zero OS commands will be run, and verifies reversibility and rollback instructions."*

---

## Scene 5: Safe Automation Execution & Verification (1.5 Minutes)

1. **Approve the Remediation Action**:
   - Return to the approval page and enter optional notes: `Approved for immediate simulated recovery.`
   - Click **Approve Action**.
2. **Trigger Safe Execution**:
   - Notice that the **SAFE AUTOMATION (Simulation Mode)** panel is now unlocked.
   - Click **Execute Approved Action**.
   - Review the output: `SUCCESS — Nginx restart simulated successfully.`
   - Emphasize that this ran strictly in-process via Python (`SAFE_ACTIONS`) without invoking any shell subprocesses.
3. **Run Post-Execution Verification**:
   - Click **Verify Execution**.
   - Point out that status transitions to **PASSED** and the ticket automatically updates to **RESOLVED** with a recorded `resolved_at` timestamp.

---

## Scene 6: Continuous Feedback & Knowledge Updates (1.0 Minute)

1. **Submit Operator Feedback**:
   - Logout and log back in as `employeee` / `employeee1234`.
   - Open the resolved incident `INC-0004`.
   - Fill in the feedback form:
     - **Rating**: `5 Stars` (or `4 Stars`)
     - **Comments**: `Nginx service recovered immediately. Runbook steps were clear and accurate.`
   - Click **Submit Feedback**.
2. **Review Knowledge Feedback as Admin**:
   - Switch back to `admin` / `admin1234`.
   - Navigate to **Knowledge Feedback** in the sidebar (`/admin-portal/runbooks/feedback/`).
   - Show the newly recorded rating and click **Update** to open the Runbook editor, showing how telemetry drives continuous procedure updates.

---

## Scene 7: Verification & Robustness Evidence (1.5 Minutes)

1. **Demonstrate Automated Test Suite**:
   - Switch to your terminal and run:
     ```bash
     .\venv\Scripts\python.exe manage.py test
     ```
   - Highlight the result:
     `Ran 120 tests in ~295s — OK (0 failures, 0 errors)`.
   - Point out that all 17 failure and robustness edge cases (empty text, unicode, unlisted actions, unauthorized access) are covered.
2. **Run the Official Benchmark Evaluation Harness**:
   - In terminal, execute:
     ```bash
     .\venv\Scripts\python.exe manage.py evaluate_aiops
     ```
   - Review live results:
     - **AIOps Retrieval Accuracy**: **98.0%** vs **86.0%** Baseline Lookup (+12.0% improvement).
     - **Citation Correctness**: **100.0%**.
     - **Unsafe Action Rejection Rate**: **100.0%** (10/10 blocked).
3. **Concluding Statement**:
   > *"Thank you. This completes our demonstration of the AIOps Service Desk, fully satisfying all functional, safety, and architectural capstone requirements."*
