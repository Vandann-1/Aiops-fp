# Engineering Evidence & Verification Report — AIOps Service Desk

This document provides concrete, verifiable proof of system health, automated testing coverage, architectural checks, CI/CD integration, and benchmark performance metrics.

---

## 1. Automated Test Suite Metrics

All tests execute in an automated in-memory SQLite sandbox without requiring external servers or mock internet access.

| Metric | Measured Value | Standard Required |
| :--- | :--- | :--- |
| **Total Automated Tests** | **120 Tests** | $\ge 100$ |
| **Test Execution Status** | **120 / 120 Passed (100% Pass Rate)** | 0 Failures, 0 Errors |
| **Test Execution Duration** | ~295 seconds | Fully automated execution |
| **Django System Check** | **0 issues identified** | Clean system integrity |
| **Database Migrations Check**| **0 pending migrations** | All models in sync with DB |

### Test Breakdown by Subsystem

```
Total: 120 tests
├── runbooks.tests: 48 tests (Phases 3 & 4)
│   ├── Runbook catalog CRUD, pagination, filtering
│   ├── Local TF-IDF & Cosine Similarity vectorization
│   ├── Minimum threshold cutoff enforcement (<0.20)
│   ├── Inactive runbook exclusion from AI retrieval
│   └── Multi-token symptom and category matching
├── automation.tests: 55 tests (Phases 5, 6, 7 & 8)
│   ├── Human-in-the-loop review state machine
│   ├── Safe action allowlist validation (SAFE_ACTIONS)
│   ├── Rejection of unauthorized OS commands / subshells
│   ├── In-process Python simulation execution
│   ├── Post-execution automated verification
│   ├── Pre-execution state checklist validation
│   └── Tamper-evident AuditLog event creation
└── incidents.tests: 17 tests (Phase 15 Robustness Suite)
    ├── Empty description handling
    ├── Unicode / special character resilience
    ├── Sub-threshold graceful non-match handling
    ├── Empty runbook database resilience
    ├── Unknown intent & service fallback
    ├── Approval gate rejection without recommendations
    ├── Inactive runbook approval rejection
    ├── Double-approval & double-rejection prevention
    ├── Unapproved execution blocking
    ├── Rejected action execution blocking
    ├── Unlisted dangerous action blocking
    ├── Simulated execution failure handling
    ├── Verification failure handling
    ├── Duplicate feedback prevention
    ├── Role-based access control unauthorized blocking
    └── Invalid primary key 404 handling
```

---

## 2. Automated Quality & System Checks

### 2.1 Django System Check
```bash
python manage.py check
```
**Output**:
```text
System check identified no issues (0 silenced).
```

### 2.2 Migrations Up-to-Date Check
```bash
python manage.py makemigrations --check --dry-run
```
**Output**:
```text
No changes detected in apps: 'accounts', 'incidents', 'runbooks', 'automation'.
```

---

## 3. Real Benchmark Evaluation Harness (`data/evaluation_results.json`)

Executed against 50 real synthetic evaluation cases spanning all infrastructure domains (`python manage.py evaluate_aiops`):

| Evaluation Dimension | Measured Score | Evaluation Methodology |
| :--- | :--- | :--- |
| **AIOps TF-IDF Retrieval Accuracy** | **98.0%** (49/50 correct) | Cosine similarity matching against expected canonical runbooks |
| **Baseline Keyword Lookup Accuracy**| **86.0%** (43/50 correct) | Direct substring keyword comparison |
| **Relative Retrieval Improvement** | **+12.0%** | Delta improvement achieved by local TF-IDF vectorization |
| **Citation Correctness Rate** | **100.0%** (49/49) | Validates that matched symptoms and cited steps correspond to runbook |
| **Unsafe Action Rejection Rate** | **100.0%** (10/10 blocked) | Rigorous probe of dangerous commands (`rm_rf`, `delete_database`, etc.) |
| **Service Classification Accuracy** | **78.0%** (39/50 correct) | Deterministic keyword and regex rule matching |
| **Intent Classification Accuracy** | **64.0%** (32/50 correct) | Rule-based intent classifier across 8 canonical intents |
| **Classified Priority Accuracy** | **64.0%** (32/50 correct) | Algorithmic SLA urgency recommendation |
| **Mean Time to Resolution (MTTR)** | *Not yet measured* | Accurately reported as unmeasured until real resolved tickets exist |

---

## 4. Continuous Integration (CI) Workflow

The automated GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request to `main`:
1. Checks out repository source code.
2. Configures a clean Python 3.11 environment.
3. Installs dependencies from `requirements.txt`.
4. Runs `python manage.py check`.
5. Runs `python manage.py makemigrations --check --dry-run`.
6. Executes all 120 unit and robustness tests with `--verbosity=2`.
7. Executes the AIOps benchmark evaluation harness (`python manage.py evaluate_aiops`).

---

## 5. Local Reproduction Steps

To reproduce the engineering evidence from a clean clone:

```bash
# 1. Clone repository
git clone https://github.com/Vandann-1/Aiops-fp.git
cd Aiops-fp

# 2. Set up virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Linux/macOS: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run system checks
python manage.py check
python manage.py makemigrations --check

# 5. Apply migrations
python manage.py migrate

# 6. Seed sample development data (Admins, Employees, Canonical Runbooks)
python setup_dev_data.py

# 7. Run full automated test suite (120 tests)
python manage.py test

# 8. Run official evaluation harness
python manage.py evaluate_aiops
```
