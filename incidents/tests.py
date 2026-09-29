from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Profile
from incidents.models import Incident, IncidentFeedback
from incidents.normalization import normalize_incident_data, classify_intent, classify_service
from runbooks.models import Runbook, RunbookRecommendation
from runbooks.retrieval import retrieve_runbooks_for_incident
from automation.models import AutomationApproval, AutomationExecution, VerificationResult, AuditLog
from automation.executor import execute_approved_action
from automation.verification import verify_execution
from automation.safety import is_action_safe, get_diagnostic_checklist

User = get_user_model()

class AIOpsRobustnessAndFailureTestSuite(TestCase):
    """
    Part 15: Failure & Robustness Tests for all 17 capstone scenarios.
    """
    def setUp(self):
        self.client = Client()
        
        # 1. Create Admin User
        self.admin = User.objects.create_user(username='admin_test', password='adminpassword')
        self.admin.profile.role = Profile.Role.IT_ADMIN
        self.admin.profile.save()

        # 2. Create Employee User
        self.employee = User.objects.create_user(username='emp_test', password='emppassword')
        self.employee.profile.role = Profile.Role.EMPLOYEE
        self.employee.profile.save()

        # 3. Create Second Employee User (for ownership checks)
        self.other_employee = User.objects.create_user(username='other_emp', password='emppassword')
        self.other_employee.profile.role = Profile.Role.EMPLOYEE
        self.other_employee.profile.save()

        # 4. Standard Allowlisted Runbook
        self.nginx_rb = Runbook.objects.create(
            runbook_number='RB-0001',
            title='Restart Nginx Web Server',
            category=Incident.Category.SERVER,
            description='Procedure for restarting Nginx web service when unreachable.',
            symptoms='Website down\nConnection refused\n502 Bad Gateway',
            steps='1. Check service status.\n2. Restart nginx.\n3. Verify HTTP 200.',
            risk_level=Runbook.RiskLevel.LOW,
            automation_action='restart_nginx',
            is_active=True,
            created_by=self.admin
        )

        # 5. Inactive Runbook
        self.inactive_rb = Runbook.objects.create(
            runbook_number='RB-0099',
            title='Legacy Retired Database Tool',
            category=Incident.Category.DATABASE,
            description='Deprecated database cleanup script.',
            symptoms='Database disk overflow',
            steps='Run manual vacuum.',
            risk_level=Runbook.RiskLevel.HIGH,
            automation_action='restart_postgresql',
            is_active=False,
            created_by=self.admin
        )

        # 6. Failure Simulation Runbook
        self.failure_rb = Runbook.objects.create(
            runbook_number='RB-0098',
            title='Simulated Failure Test Hook',
            category=Incident.Category.OTHER,
            description='Diagnostics for simulated failure hook.',
            symptoms='Simulated system failure condition',
            steps='Trigger mock failure.',
            risk_level=Runbook.RiskLevel.LOW,
            automation_action='simulate_failure',
            is_active=True,
            created_by=self.admin
        )

        # 7. Verification Failure Simulation Runbook
        self.verif_fail_rb = Runbook.objects.create(
            runbook_number='RB-0097',
            title='Simulated Verification Failure Test Hook',
            category=Incident.Category.OTHER,
            description='Diagnostics for simulated verification failure.',
            symptoms='Simulated verification check failure condition',
            steps='Trigger mock verification failure.',
            risk_level=Runbook.RiskLevel.LOW,
            automation_action='simulate_verification_failure',
            is_active=True,
            created_by=self.admin
        )

    # 1. Incident with empty description -> handled gracefully
    def test_01_incident_empty_description_handled_gracefully(self):
        norm = normalize_incident_data(title="Server unreachable", description="")
        self.assertIsNotNone(norm)
        self.assertIn("intent", norm)
        self.assertIn("service", norm)
        
        inc = Incident.objects.create(
            title="Server unreachable",
            description="",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        self.assertTrue(inc.incident_number.startswith("INC-"))
        self.assertTrue(len(inc.normalized_description) > 0)
        self.assertIn("Server unreachable", inc.normalized_description)

    # 2. Incident with special characters / unicode -> handled gracefully
    def test_02_incident_special_characters_and_unicode_handled_gracefully(self):
        complex_text = "CRITICAL: Nginx 502 Bad Gateway! 💥🔥 #@$%^&*() — /var/log/nginx/error.log NULL\x00 byte test [ümlaut: äöüß]"
        norm = normalize_incident_data(title="Web Gateway Crash", description=complex_text)
        self.assertIsNotNone(norm)
        self.assertEqual(norm["service"], "Web Server")
        
        inc = Incident.objects.create(
            title="Unicode crash test 🔥",
            description=complex_text,
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        self.assertEqual(inc.service, "Web Server")
        self.assertIn("502 Bad Gateway", inc.normalized_description)

    # 3. Incident that matches no runbook (similarity < threshold) -> handled gracefully
    def test_03_incident_no_runbook_match_below_threshold(self):
        inc = Incident.objects.create(
            title="Quantum entanglement interference on subspace array",
            description="Tachyon particle fluctuations detected in warp nacelles.",
            category=Incident.Category.OTHER,
            created_by=self.employee
        )
        rec = retrieve_runbooks_for_incident(inc)
        self.assertIsNone(rec["runbook"])
        self.assertLess(rec["score"], 0.20)

    # 4. Retrieval with empty runbook database -> handled gracefully, returns no recommendation
    def test_04_retrieval_empty_runbook_database(self):
        Runbook.objects.all().delete()
        inc = Incident.objects.create(
            title="Nginx down",
            description="Website is completely offline.",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        rec = retrieve_runbooks_for_incident(inc)
        self.assertIsNone(rec["runbook"])
        self.assertEqual(rec["score"], 0.0)
        self.assertEqual(rec["top_matches"], [])

    # 5. Triage with unknown intent/service -> defaults to Unknown, does not crash
    def test_05_triage_unknown_intent_and_service(self):
        intent = classify_intent("Random text xyz completely unparseable gibberish 12345")
        service = classify_service("Random text xyz completely unparseable gibberish 12345")
        self.assertEqual(intent, "Unknown")
        self.assertEqual(service, "Unknown")

    # 6. Attempt to request approval for incident with no recommendation -> rejected with error
    def test_06_request_approval_no_recommendation_rejected(self):
        inc = Incident.objects.create(
            title="Incident without AI recommendation",
            description="Testing approval rejection when no runbook is recommended.",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        self.client.login(username='admin_test', password='adminpassword')
        url = reverse('admin_incident_request_approval', kwargs={'pk': inc.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AutomationApproval.objects.filter(incident=inc).exists())

    # 7. Attempt to request approval for incident with inactive runbook -> rejected with error
    def test_07_request_approval_inactive_runbook_rejected(self):
        inc = Incident.objects.create(
            title="Database cleanup needed",
            description="Database disk overflow requiring cleanup.",
            category=Incident.Category.DATABASE,
            created_by=self.employee
        )
        RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.inactive_rb,
            match_score=0.95
        )
        self.client.login(username='admin_test', password='adminpassword')
        url = reverse('admin_incident_request_approval', kwargs={'pk': inc.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AutomationApproval.objects.filter(incident=inc).exists())

    # 8. Attempt to approve already approved request -> rejected with error
    def test_08_approve_already_approved_request_rejected(self):
        inc = Incident.objects.create(
            title="Nginx outage",
            description="Website down 502 Bad Gateway",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            match_score=0.90
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_by=self.admin
        )
        self.client.login(username='admin_test', password='adminpassword')
        url = reverse('approve_action', kwargs={'pk': approval.pk})
        response = self.client.post(url, {'reason': 'Second approval attempt'})
        self.assertEqual(response.status_code, 302)

    # 9. Attempt to approve already rejected request -> rejected with error
    def test_09_approve_already_rejected_request_rejected(self):
        inc = Incident.objects.create(
            title="Nginx outage",
            description="Website down 502 Bad Gateway",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            match_score=0.90
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.REJECTED,
            reviewed_by=self.admin,
            reason='Unsafe timing'
        )
        self.client.login(username='admin_test', password='adminpassword')
        url = reverse('approve_action', kwargs={'pk': approval.pk})
        response = self.client.post(url, {'reason': 'Re-approving rejected'})
        self.assertEqual(response.status_code, 302)
        approval.refresh_from_db()
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.REJECTED)

    # 10. Attempt to execute without approval -> blocked, AuditLog created
    def test_10_execute_without_approval_blocked(self):
        inc = Incident.objects.create(
            title="Nginx failure",
            description="Nginx down",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.PENDING
        )
        execution = execute_approved_action(approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertTrue(AuditLog.objects.filter(
            incident=inc,
            event_type=AuditLog.EventType.AUTOMATION_BLOCKED
        ).exists())

    # 11. Attempt to execute rejected action -> blocked, AuditLog created
    def test_11_execute_rejected_action_blocked(self):
        inc = Incident.objects.create(
            title="Nginx failure",
            description="Nginx down",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.REJECTED,
            reason='Rejected due to freeze window'
        )
        execution = execute_approved_action(approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertTrue(AuditLog.objects.filter(
            incident=inc,
            event_type=AuditLog.EventType.AUTOMATION_BLOCKED
        ).exists())

    # 12. Attempt to execute unlisted action -> blocked, AuditLog created
    def test_12_execute_unlisted_action_blocked(self):
        unlisted_rb = Runbook.objects.create(
            runbook_number='RB-9999',
            title='Delete Production Database',
            category=Incident.Category.DATABASE,
            description='Unsafe command',
            symptoms='Errors',
            steps='Drop all',
            risk_level=Runbook.RiskLevel.HIGH,
            automation_action='delete_database',
            is_active=True,
            created_by=self.admin
        )
        inc = Incident.objects.create(
            title="Database cleanup",
            description="Database down",
            category=Incident.Category.DATABASE,
            created_by=self.employee
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=unlisted_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.APPROVED
        )
        execution = execute_approved_action(approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertIn("allowlist", execution.error_message.lower())
        self.assertTrue(AuditLog.objects.filter(
            incident=inc,
            event_type=AuditLog.EventType.AUTOMATION_BLOCKED
        ).exists())

    # 13. Simulated execution failure -> error recorded, incident not resolved
    def test_13_simulated_execution_failure_handled(self):
        inc = Incident.objects.create(
            title="Failure test incident",
            description="Testing simulation failure handling.",
            category=Incident.Category.OTHER,
            created_by=self.employee
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.failure_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.APPROVED
        )
        execution = execute_approved_action(approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.FAILED)
        self.assertIn("Simulated action failure", execution.error_message)
        inc.refresh_from_db()
        self.assertNotEqual(inc.status, Incident.Status.RESOLVED)

    # 14. Verification failure -> failure recorded, incident remains open
    def test_14_verification_failure_leaves_incident_open(self):
        inc = Incident.objects.create(
            title="Verification failure test incident",
            description="Testing verification failure check.",
            category=Incident.Category.OTHER,
            status=Incident.Status.IN_PROGRESS,
            created_by=self.employee
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.verif_fail_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.APPROVED
        )
        execution = execute_approved_action(approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.SUCCESS)

        is_passed, verification, msg = verify_execution(execution, actor=self.admin)
        self.assertFalse(is_passed)
        self.assertEqual(verification.status, VerificationResult.Status.FAILED)
        inc.refresh_from_db()
        self.assertNotEqual(inc.status, Incident.Status.RESOLVED)

    # 15. Duplicate feedback submission -> rejected with error
    def test_15_duplicate_feedback_submission_rejected(self):
        inc = Incident.objects.create(
            title="Resolved incident with feedback",
            description="Feedback testing.",
            category=Incident.Category.SERVER,
            status=Incident.Status.RESOLVED,
            created_by=self.employee
        )
        IncidentFeedback.objects.create(
            incident=inc,
            user=self.employee,
            rating=5,
            comment="Excellent fix!"
        )
        self.client.login(username='emp_test', password='emppassword')
        url = reverse('employee_submit_feedback', kwargs={'pk': inc.pk})
        response = self.client.post(url, {'rating': 4, 'comment': 'Second rating attempt'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IncidentFeedback.objects.filter(incident=inc).count(), 1)

    # 16. Unauthorized user accessing approval endpoints -> 403 Forbidden or redirect
    def test_16_unauthorized_user_accessing_admin_endpoints(self):
        inc = Incident.objects.create(
            title="Restricted admin incident",
            description="Testing employee access prevention.",
            category=Incident.Category.SERVER,
            created_by=self.employee
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.nginx_rb,
            requested_by=self.admin,
            status=AutomationApproval.ApprovalStatus.PENDING
        )
        # Logged in as regular employee (not IT Admin)
        self.client.login(username='emp_test', password='emppassword')
        
        # Try accessing approval detail
        resp_detail = self.client.get(reverse('approval_detail', kwargs={'pk': approval.pk}))
        self.assertIn(resp_detail.status_code, [302, 403])
        
        # Try approving action
        resp_approve = self.client.post(reverse('approve_action', kwargs={'pk': approval.pk}))
        self.assertIn(resp_approve.status_code, [302, 403])

        # Try dry-run view
        resp_dry_run = self.client.get(reverse('admin_approval_dry_run', kwargs={'pk': approval.pk}))
        self.assertIn(resp_dry_run.status_code, [302, 403])

    # 17. Invalid incident ID in URL -> 404 Not Found
    def test_17_invalid_incident_id_returns_404(self):
        self.client.login(username='admin_test', password='adminpassword')
        invalid_url = reverse('admin_incident_detail', kwargs={'pk': 999999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
