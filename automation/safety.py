"""
Safety Allowlist & Diagnostic Checklist Service for Phase 6.

This module validates that automation actions adhere strictly to safety constraints:
- Only predefined, simulated Python actions in SAFE_ACTIONS are permitted.
- Operating system shells, subprocesses, exec, eval, and destructive commands are blocked.
- Human approval is required prior to execution.
- Generates transparent, verifiable diagnostic safety checklists based on live system state.
"""

from automation.actions import SAFE_ACTIONS, get_action_metadata
from automation.models import AutomationApproval
from incidents.models import Incident

# Explicit Safe Action Allowlist
SAFE_ACTIONS_ALLOWLIST = list(SAFE_ACTIONS.keys())

# Standard Unsafe Action Prohibited Patterns (for evaluation and tests)
UNSAFE_ACTIONS = [
    "delete_database",
    "drop_table",
    "shutdown_server",
    "delete_files",
    "rm_rf",
    "kill_process",
    "exec_shell",
    "format_disk",
    "dump_credentials",
    "unknown_command"
]


def is_action_safe(action_name):
    """
    Validates whether an action name exists within the safe allowlist.
    """
    return bool(action_name and action_name in SAFE_ACTIONS)


def get_diagnostic_checklist(incident, approval=None):
    """
    Part 6: Builds a lightweight diagnostic checklist before automation execution.
    Evaluates real system state to determine whether execution can safely proceed.
    
    Checks:
    1. Incident has a recommended/approved runbook
    2. Runbook is active
    3. Automation action exists
    4. Action is in safe allowlist
    5. Incident is not resolved
    6. Required approval exists
    7. Action is simulation-safe
    """
    rec = getattr(incident, 'runbook_recommendation', None)
    runbook = None
    if approval and approval.runbook:
        runbook = approval.runbook
    elif rec and rec.runbook:
        runbook = rec.runbook

    action_name = runbook.automation_action if runbook else ""
    is_safe = bool(action_name and action_name in SAFE_ACTIONS)

    # 1. Incident has an approved/recommended runbook
    c1_passed = bool(runbook is not None)
    c1_detail = f"Runbook {runbook.runbook_number} attached" if c1_passed else "No runbook attached"

    # 2. Runbook is active
    c2_passed = bool(runbook and runbook.is_active)
    c2_detail = "Runbook is active in knowledge base" if c2_passed else "Runbook is inactive or missing"

    # 3. Automation action exists
    c3_passed = bool(action_name)
    c3_detail = f"Action hook: '{action_name}'" if c3_passed else "No automation action configured"

    # 4. Action is in safe allowlist
    c4_passed = is_safe
    c4_detail = "Action verified in SAFE_ACTIONS allowlist" if c4_passed else "Action NOT in safe allowlist"

    # 5. Incident is not resolved
    c5_passed = bool(incident and incident.status != Incident.Status.RESOLVED)
    c5_detail = "Incident is open / eligible for automation" if c5_passed else "Incident is already resolved"

    # 6. Required approval exists
    c6_passed = bool(approval and approval.status == AutomationApproval.ApprovalStatus.APPROVED)
    if approval:
        c6_detail = f"Approval #{approval.id} status is {approval.get_status_display()}"
    else:
        c6_detail = "No human approval request found"

    # 7. Action is simulation-safe
    c7_passed = bool(is_safe and action_name in SAFE_ACTIONS)
    c7_detail = "In-process Python simulation (no OS subprocess/shell)" if c7_passed else "Action not confirmed simulation-safe"

    items = [
        {"id": "runbook_exists", "label": "Incident has an approved runbook", "passed": c1_passed, "detail": c1_detail},
        {"id": "runbook_active", "label": "Runbook is active", "passed": c2_passed, "detail": c2_detail},
        {"id": "action_exists", "label": "Automation action exists", "passed": c3_passed, "detail": c3_detail},
        {"id": "action_allowlisted", "label": "Action is in safe allowlist", "passed": c4_passed, "detail": c4_detail},
        {"id": "incident_unresolved", "label": "Incident is not resolved", "passed": c5_passed, "detail": c5_detail},
        {"id": "approval_granted", "label": "Required approval exists", "passed": c6_passed, "detail": c6_detail},
        {"id": "simulation_safe", "label": "Action is simulation-safe", "passed": c7_passed, "detail": c7_detail},
    ]

    all_passed = all(item["passed"] for item in items)
    passed_count = sum(1 for item in items if item["passed"])

    return {
        "items": items,
        "all_passed": all_passed,
        "passed_count": passed_count,
        "total_count": len(items),
        "action_metadata": get_action_metadata(action_name) if action_name else None
    }
