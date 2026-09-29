"""
Evaluation Harness Command for AIOps Service Desk Capstone.

Measures:
1. Triage Accuracy (Intent, Service, Priority)
2. Runbook Retrieval Accuracy (TF-IDF vs Baseline)
3. Retrieval Citation Correctness
4. Unsafe Action Rejection Rate (Experiment)
5. Approved Automation Success Rate
6. Mean Resolution Time
7. User Feedback Rating

Usage:
    python manage.py evaluate_aiops
"""

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Avg
from incidents.models import Incident, IncidentFeedback
from runbooks.models import Runbook
from runbooks.retrieval import retrieve_best_runbook
from incidents.normalization import normalize_incident_data
from automation.models import AutomationApproval, AutomationExecution, AuditLog
from automation.executor import validate_automation
from automation.safety import UNSAFE_ACTIONS


class DummyIncident:
    """Mock incident wrapper for running evaluation cases against retrieval engine."""
    def __init__(self, title, description, category, intent="", service=""):
        self.id = 99999
        self.incident_number = "INC-EVAL"
        self.title = title
        self.description = description
        self.category = category
        self.intent = intent
        self.service = service
        self.priority = Incident.Priority.MEDIUM
        self.status = Incident.Status.OPEN


def baseline_lookup(title, description, category, active_runbooks):
    """
    Baseline Method: Naive keyword search matching title words against runbook title and category.
    Represents traditional manual runbook lookup without semantic TF-IDF vectorization.
    """
    query_words = set(f"{title} {description}".lower().split())
    best_rb = None
    best_overlap = 0

    for rb in active_runbooks:
        score = 0
        if rb.category == category:
            score += 2
        rb_words = set(f"{rb.title} {rb.description}".lower().split())
        overlap = len(query_words.intersection(rb_words))
        score += overlap

        if score > best_overlap:
            best_overlap = score
            best_rb = rb

    return best_rb


class Command(BaseCommand):
    help = "Evaluates the AIOps Service Desk on accuracy, retrieval, safety, and operational metrics."

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(" AIOPS SERVICE DESK - CAPSTONE EVALUATION HARNESS")
        self.stdout.write("=" * 70)

        # 1. Load Evaluation Cases
        eval_path = os.path.join(settings.BASE_DIR, 'data', 'evaluation_cases.json')
        if not os.path.exists(eval_path):
            self.stderr.write(f"Evaluation cases file not found at {eval_path}")
            return

        with open(eval_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)

        total_cases = len(cases)
        self.stdout.write(f"Loaded {total_cases} synthetic evaluation test cases.")

        active_runbooks = list(Runbook.objects.filter(is_active=True))
        if not active_runbooks:
            self.stderr.write("No active runbooks in database. Run `python setup_dev_data.py` first.")
            return

        self.stdout.write(f"Active runbooks in knowledge base: {len(active_runbooks)}")
        self.stdout.write("-" * 70)

        # ----------------------------------------------------
        # METRIC 1: TRIAGE ACCURACY
        # ----------------------------------------------------
        intent_correct = 0
        service_correct = 0
        priority_correct = 0
        combined_triage_correct = 0

        for case in cases:
            norm = normalize_incident_data(case['title'], case['description'], category=case.get('category'))
            
            i_match = (norm['intent'].lower() == case['expected_intent'].lower())
            s_match = (norm['service'].lower() == case['expected_service'].lower())
            p_match = (norm['classified_priority'].upper() == case['expected_priority'].upper())

            if i_match:
                intent_correct += 1
            if s_match:
                service_correct += 1
            if p_match:
                priority_correct += 1
            if i_match and s_match and p_match:
                combined_triage_correct += 1

        intent_acc = (intent_correct / total_cases) * 100
        service_acc = (service_correct / total_cases) * 100
        priority_acc = (priority_correct / total_cases) * 100
        overall_triage_acc = (combined_triage_correct / total_cases) * 100

        self.stdout.write(self.style.SUCCESS("[1] TRIAGE CLASSIFICATION ACCURACY:"))
        self.stdout.write(f"    - Intent Accuracy:       {intent_correct}/{total_cases} ({intent_acc:.1f}%)")
        self.stdout.write(f"    - Service Accuracy:      {service_correct}/{total_cases} ({service_acc:.1f}%)")
        self.stdout.write(f"    - Priority Accuracy:     {priority_correct}/{total_cases} ({priority_acc:.1f}%)")
        self.stdout.write(f"    - Combined All-Match:    {combined_triage_correct}/{total_cases} ({overall_triage_acc:.1f}%)")
        self.stdout.write("-" * 70)

        # ----------------------------------------------------
        # METRIC 2: RUNBOOK RETRIEVAL ACCURACY (BASELINE VS AIOPS)
        # ----------------------------------------------------
        baseline_hits = 0
        aiops_hits = 0
        citation_correct = 0

        for case in cases:
            # Baseline manual/keyword retrieval
            base_rb = baseline_lookup(case['title'], case['description'], case.get('category'), active_runbooks)
            if base_rb and base_rb.title.lower() == case['expected_runbook'].lower():
                baseline_hits += 1

            # AIOps TF-IDF retrieval
            mock_inc = DummyIncident(
                title=case['title'],
                description=case['description'],
                category=case.get('category'),
                intent=case.get('expected_intent', ''),
                service=case.get('expected_service', '')
            )
            result = retrieve_best_runbook(mock_inc)
            aiops_rb = result.get('runbook')
            
            if aiops_rb and aiops_rb.title.lower() == case['expected_runbook'].lower():
                aiops_hits += 1

                # Metric 3: Citation correctness
                citation = result.get('citation', {})
                if citation.get('citation_reference') and len(citation.get('matched_symptoms', [])) > 0:
                    citation_correct += 1

        baseline_acc = (baseline_hits / total_cases) * 100
        aiops_acc = (aiops_hits / total_cases) * 100
        citation_rate = (citation_correct / max(aiops_hits, 1)) * 100

        self.stdout.write(self.style.SUCCESS("[2] RUNBOOK RETRIEVAL COMPARISON (BASELINE VS AIOPS):"))
        self.stdout.write(f"    - Baseline Manual Lookup Accuracy:  {baseline_hits}/{total_cases} ({baseline_acc:.1f}%)")
        self.stdout.write(f"    - AIOps TF-IDF Retrieval Accuracy:   {aiops_hits}/{total_cases} ({aiops_acc:.1f}%)")
        self.stdout.write(f"    - Relative Retrieval Improvement:    +{aiops_acc - baseline_acc:.1f}%")
        self.stdout.write("-" * 70)

        # ----------------------------------------------------
        # METRIC 3: RETRIEVAL CITATION CORRECTNESS
        # ----------------------------------------------------
        self.stdout.write(self.style.SUCCESS("[3] RUNBOOK CITATION & EVIDENCE ACCURACY:"))
        self.stdout.write(f"    - Correct Citations Generated:       {citation_correct}/{aiops_hits} ({citation_rate:.1f}%)")
        self.stdout.write("-" * 70)

        # ----------------------------------------------------
        # METRIC 4: UNSAFE ACTION EXPERIMENT (Part 14)
        # ----------------------------------------------------
        blocked_count = 0
        total_unsafe_attempts = len(UNSAFE_ACTIONS)

        # Mock approval structure with unsafe action
        class MockRunbook:
            def __init__(self, action):
                self.automation_action = action
                self.is_active = True

        class MockIncident:
            status = Incident.Status.APPROVED

        class MockApproval:
            status = AutomationApproval.ApprovalStatus.APPROVED
            def __init__(self, action):
                self.incident = MockIncident()
                self.runbook = MockRunbook(action)

        for unsafe_act in UNSAFE_ACTIONS:
            mock_app = MockApproval(unsafe_act)
            is_valid, reason = validate_automation(mock_app)
            if not is_valid and "allowlist" in str(reason).lower():
                blocked_count += 1

        rejection_rate = (blocked_count / total_unsafe_attempts) * 100
        self.stdout.write(self.style.SUCCESS("[4] UNSAFE ACTION EXPERIMENT (REJECTION RATE):"))
        self.stdout.write(f"    - Unsafe Actions Evaluated:          {total_unsafe_attempts}")
        self.stdout.write(f"    - Unsafe Actions Blocked by Policy:  {blocked_count}")
        self.stdout.write(f"    - Unsafe Action Rejection Rate:      {rejection_rate:.1f}% (Expected: 100.0%)")
        self.stdout.write("-" * 70)

        # ----------------------------------------------------
        # METRICS 5, 6, 7: OPERATIONAL METRICS FROM DB
        # ----------------------------------------------------
        # Automation Executions
        execs_success = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.SUCCESS).count()
        execs_failed = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.FAILED).count()
        total_execs = execs_success + execs_failed
        automation_success_pct = (execs_success / total_execs * 100) if total_execs > 0 else "Not yet measured"

        # Mean Resolution Time
        resolved_incidents = Incident.objects.filter(status=Incident.Status.RESOLVED, resolved_at__isnull=False)
        total_sec = sum((inc.resolved_at - inc.created_at).total_seconds() for inc in resolved_incidents if inc.resolved_at and inc.created_at)
        mean_time_str = f"{round(total_sec / (resolved_incidents.count() * 60), 1)} minutes" if resolved_incidents.count() > 0 else "Not yet measured"

        # User Feedback
        feedbacks = IncidentFeedback.objects.all()
        avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg']
        avg_rating_str = f"{round(avg_rating, 2)} / 5.0 (from {feedbacks.count()} ratings)" if avg_rating is not None else "Not yet measured"

        self.stdout.write(self.style.SUCCESS("[5] APPROVED AUTOMATION SUCCESS RATE:"))
        self.stdout.write(f"    - Executions Success Rate:           {automation_success_pct if isinstance(automation_success_pct, str) else f'{automation_success_pct:.1f}%'} ({execs_success} success, {execs_failed} failed)")

        self.stdout.write(self.style.SUCCESS("[6] MEAN RESOLUTION TIME (MTTR):"))
        self.stdout.write(f"    - Average Resolution Time:           {mean_time_str} ({resolved_incidents.count()} resolved tickets)")

        self.stdout.write(self.style.SUCCESS("[7] USER FEEDBACK MEASUREMENT:"))
        self.stdout.write(f"    - Average Runbook Usefulness:        {avg_rating_str}")
        self.stdout.write("=" * 70)

        # Save results to data/evaluation_results.json for UI presentation
        results_data = {
            "total_cases": total_cases,
            "intent_accuracy": round(intent_acc, 1),
            "service_accuracy": round(service_acc, 1),
            "priority_accuracy": round(priority_acc, 1),
            "overall_triage_accuracy": round(overall_triage_acc, 1),
            "baseline_retrieval_accuracy": round(baseline_acc, 1),
            "aiops_retrieval_accuracy": round(aiops_acc, 1),
            "retrieval_improvement": round(aiops_acc - baseline_acc, 1),
            "citation_correctness_rate": round(citation_rate, 1),
            "unsafe_actions_tested": total_unsafe_attempts,
            "unsafe_actions_blocked": blocked_count,
            "unsafe_action_rejection_rate": round(rejection_rate, 1),
            "automation_success_rate": round(automation_success_pct, 1) if isinstance(automation_success_pct, float) else None,
            "mean_resolution_time": mean_time_str,
            "user_feedback_average": round(avg_rating, 2) if avg_rating is not None else None,
            "feedback_count": feedbacks.count(),
        }

        results_file = os.path.join(settings.BASE_DIR, 'data', 'evaluation_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Evaluation report successfully saved to {results_file}"))
