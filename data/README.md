# Synthetic Evaluation Dataset Package

## 1. Dataset Purpose
This package provides a standardized, reproducible synthetic evaluation dataset for benchmarking the AIOps Service Desk capstone implementation:
- Incident Ticket Ingestion & Normalization
- Intent, Service, and Priority Classification
- TF-IDF + Cosine Similarity Local Runbook Retrieval vs. Baseline Lookup
- Retrieval Evidence & Citation Verification
- Safe Automation Allowlist Verification & Unsafe Action Rejection
- Controlled Failure & Robustness Scenarios

## 2. Strict Synthetic & Privacy Guarantees
- **No Real Customer Data**: All incident titles, descriptions, reporter identifiers, and network addresses are 100% synthetically generated.
- **No Production Secrets**: No passwords, tokens, API keys, or operational environment credentials are included.
- **In-Process Simulation**: Automation actions reference safe, in-process Python simulation mocks (no operating system commands, subprocesses, subshells, exec, or eval).

## 3. Package Structure
```
data/
├── incidents.json            # 12 representative synthetic incidents for demonstration and testing
├── runbooks.json             # 12 standard operational runbooks (RB-0001 through RB-0012)
├── evaluation_cases.json     # 50 controlled evaluation test cases for quantitative benchmarking
└── README.md                 # Dataset documentation, field descriptions, and evaluation methodology
```

## 4. Schema & Field Definitions

### `incidents.json`
| Field | Type | Description |
|---|---|---|
| `id` | String | Synthetic incident identifier (e.g., `INC-SYN-001`) |
| `title` | String | Summary issue headline |
| `description` | String | Detailed symptom description |
| `category` | String | Incident category (`SERVER`, `DATABASE`, `NETWORK`, `STORAGE`, `SECURITY`, `APPLICATION`) |
| `priority` | String | Initial reported priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) |
| `expected_intent` | String | Ground-truth normalized intent |
| `expected_service` | String | Ground-truth affected infrastructure service |
| `expected_priority` | String | Ground-truth triage priority (`P1`, `P2`, `P3`, `P4`) |
| `expected_runbook` | String | Ground-truth matching runbook title |

### `runbooks.json`
| Field | Type | Description |
|---|---|---|
| `runbook_number` | String | Unique runbook identifier (`RB-0001` to `RB-0012`) |
| `title` | String | Runbook procedure name |
| `category` | String | Target service domain |
| `description` | String | Scope and purpose statement |
| `symptoms` | String | Indicative trigger conditions (newline-separated) |
| `steps` | String | Sequenced recovery steps (newline-separated) |
| `risk_level` | String | Operational risk rating (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) |
| `automation_action` | String | Predefined safe in-process action hook |

### `evaluation_cases.json`
Contains 50 diverse synthetic test scenarios across 6 categories, providing balanced coverage of common data center incidents:
- Web Server Outages (Apache, Nginx)
- Database Failures (PostgreSQL, MySQL)
- Storage Capacity Pressure (Disk Space)
- Network Disruptions & DNS Resolution Anomalies
- Application Process Failures & Stale Cache Serving
- TLS/SSL Certificate Expiration Warnings
- High CPU and Memory Pressure Scenarios

## 5. Evaluation Usage
Run the automated evaluation harness using the Django management command:
```bash
python manage.py evaluate_aiops
```
This evaluates triage accuracy, TF-IDF retrieval accuracy vs. manual keyword baseline, citation correctness, and unsafe action rejection rate against the 50 synthetic test cases.
