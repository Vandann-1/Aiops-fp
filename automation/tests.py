import os
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from accounts.models import Profile
from incidents.models import Incident, IncidentActivity
from runbooks.models import Runbook, RunbookRecommendation
from automation.models import AutomationApproval, AutomationExecution, VerificationResult
from automation.actions import SAFE_ACTIONS

User = get_user_model()

class Phase6SafeAutomationTests(TestCase):
    def setUp(self):
        # 1. Create IT Admin user
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_user.profile.role = Profile.Role.IT_ADMIN
        self.admin_user.profile.save()

        # 2. Create Employee user
        self.employee = User.objects.create_user(username='employee', password='employeepassword')
        self.employee.profile.role = Profile.Role.EMPLOYEE
        self.employee.profile.save()

        # 3. Seed an active, allowlisted runbook
        self.runbook = Runbook.objects.create(
            title='Restart Nginx Web Server',
            category=Incident.Category.SERVER,
            description='Procedure for recovering Nginx.',
            symptoms='Nginx down',
            steps='Restart nginx',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='restart_nginx',
            created_by=self.admin_user,
            is_active=True
        )

        # 4. Seed a runbook with an unallowlisted action
        self.unknown_runbook = Runbook.objects.create(
            title='Dangerous Task',
            category=Incident.Category.SERVER,
            description='Procedure with unallowlisted action.',
            symptoms='Risk',
            steps='Destroy',
            risk_level=Runbook.RiskLevel.HIGH,
            automation_action='delete_database',
            created_by=self.admin_user,
            is_active=True
        )

        # 5. Create Incident
        self.incident = Incident.objects.create(
            title='Nginx Service Down',
            description='Nginx is down.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )

        # 6. Recommendation
        self.recommendation = RunbookRecommendation.objects.create(
            incident=self.incident,
            runbook=self.runbook,
            match_score=0.9
        )

        # 7. Approval
        self.approval = AutomationApproval.objects.create(
            incident=self.incident,
            runbook=self.runbook,
            requested_by=self.admin_user,
            reviewed_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_at=timezone.now()
        )

    # TEST 1: Approved approval + safe action -> Expected: SUCCESS
    def test_01_approved_approval_safe_action_success(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=self.approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.SUCCESS)
        self.assertEqual(execution.action_name, 'restart_nginx')
        self.assertIn("Nginx restart simulated successfully.", execution.output)

    # TEST 2: Pending approval -> Expected: execution blocked
    def test_02_pending_approval_blocked(self):
        pending_incident = Incident.objects.create(
            title='Pending Incident',
            description='Pending.',
            category=Incident.Category.SERVER,
            created_by=self.employee,
            status=Incident.Status.PENDING_APPROVAL
        )
        pending_approval = AutomationApproval.objects.create(
            incident=pending_incident,
            runbook=self.runbook,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.PENDING
        )

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': pending_approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=pending_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Approval status must be APPROVED.")

    # TEST 3: Rejected approval -> Expected: execution blocked
    def test_03_rejected_approval_blocked(self):
        rejected_incident = Incident.objects.create(
            title='Rejected Incident',
            description='Rejected.',
            category=Incident.Category.SERVER,
            created_by=self.employee,
            status=Incident.Status.REJECTED
        )
        rejected_approval = AutomationApproval.objects.create(
            incident=rejected_incident,
            runbook=self.runbook,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.REJECTED
        )

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': rejected_approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=rejected_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Approval status must be APPROVED.")

    # TEST 4: Inactive runbook -> Expected: execution blocked
    def test_04_inactive_runbook_blocked(self):
        self.runbook.is_active = False
        self.runbook.save()

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=self.approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Runbook is no longer active.")

        self.runbook.is_active = True
        self.runbook.save()

    # TEST 5: Unknown unsafe action (delete_database) -> Expected: BLOCKED
    def test_05_unknown_unsafe_action_blocked(self):
        unknown_incident = Incident.objects.create(
            title='Dangerous Action Ticket',
            description='Contains unsafe script hook.',
            category=Incident.Category.SERVER,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )
        unknown_approval = AutomationApproval.objects.create(
            incident=unknown_incident,
            runbook=self.unknown_runbook,
            requested_by=self.admin_user,
            reviewed_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_at=timezone.now()
        )

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': unknown_approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=unknown_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Action is not present in the approved automation allowlist.")

    # TEST 6: Employee tries execution endpoint -> Expected: denied
    def test_06_employee_execution_denied(self):
        client = Client()
        client.login(username='employee', password='employeepassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

    # TEST 7: Unauthenticated user -> Expected: redirect/login denial
    def test_07_unauthenticated_user_denied(self):
        client = Client()
        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # TEST 8: GET request to execute endpoint -> Expected: must not execute (405)
    def test_08_get_request_must_not_execute(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(AutomationExecution.objects.filter(approval=self.approval).exists())

    # TEST 9: Valid Admin POST -> Expected: execution occurs
    def test_09_valid_admin_post_executes(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AutomationExecution.objects.filter(approval=self.approval).exists())

    # TEST 10: Duplicate execution after SUCCESS -> Expected: second execution blocked
    def test_10_duplicate_execution_blocked(self):
        # First execution SUCCESS
        AutomationExecution.objects.create(
            approval=self.approval,
            action_name='restart_nginx',
            status=AutomationExecution.ExecutionStatus.SUCCESS,
            output="Original output",
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        # Still exactly 1 record and output untouched
        self.assertEqual(AutomationExecution.objects.filter(approval=self.approval).count(), 1)
        execution = AutomationExecution.objects.get(approval=self.approval)
        self.assertEqual(execution.output, "Original output")

    # TEST 11: Simulation function failure -> Expected: FAILED
    def test_11_simulation_function_failure(self):
        failing_runbook = Runbook.objects.create(
            title='Failing Task',
            category=Incident.Category.SERVER,
            description='Procedure with failing action.',
            symptoms='Fail',
            steps='Fail',
            risk_level=Runbook.RiskLevel.HIGH,
            automation_action='simulate_failure',
            created_by=self.admin_user,
            is_active=True
        )
        failing_incident = Incident.objects.create(
            title='Failing Action Ticket',
            description='Failing.',
            category=Incident.Category.SERVER,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )
        failing_approval = AutomationApproval.objects.create(
            incident=failing_incident,
            runbook=failing_runbook,
            requested_by=self.admin_user,
            reviewed_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_at=timezone.now()
        )

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': failing_approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=failing_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.FAILED)
        self.assertEqual(execution.error_message, "Simulation failed: Simulated action failure.")
        self.assertIsNotNone(execution.completed_at)

    # TEST 12: Successful execution -> Expected: incident NOT automatically RESOLVED
    def test_12_successful_execution_does_not_resolve_incident(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertNotEqual(self.incident.status, Incident.Status.RESOLVED)
        self.assertEqual(self.incident.status, Incident.Status.APPROVED)

    # TEST 13: Execution result saved in database
    def test_13_execution_result_saved_in_database(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        client.post(url)

        execution = AutomationExecution.objects.filter(approval=self.approval).first()
        self.assertIsNotNone(execution)
        self.assertEqual(execution.action_name, 'restart_nginx')
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.SUCCESS)
        self.assertTrue(len(execution.output) > 0)

    # TEST 14: started_at and completed_at correctly recorded
    def test_14_started_at_and_completed_at_recorded(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        client.post(url)

        execution = AutomationExecution.objects.get(approval=self.approval)
        self.assertIsNotNone(execution.started_at)
        self.assertIsNotNone(execution.completed_at)
        self.assertTrue(execution.started_at <= execution.completed_at)

    # TEST 15: Action is taken from runbook and NOT POST input
    def test_15_action_taken_from_runbook_not_post_input(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Attacker injects dangerous action parameter in POST data
        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url, data={'action': 'delete_database'})
        self.assertEqual(response.status_code, 302)

        execution = AutomationExecution.objects.get(approval=self.approval)
        # Should execute restart_nginx from the runbook and ignore 'delete_database'
        self.assertEqual(execution.action_name, 'restart_nginx')
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.SUCCESS)

    # TEST 16: Existing Phase 1–5 workflows still work
    def test_16_phase1_to_5_workflows_intact(self):
        client = Client()

        # Phase 1: Authentication & Role Check
        client.login(username='employee', password='employeepassword')
        resp = client.get(reverse('employee_dashboard'))
        self.assertEqual(resp.status_code, 200)

        # Phase 2: Create Incident
        inc_resp = client.post(reverse('employee_incident_create'), {
            'title': 'Nginx server unavailable',
            'category': 'SERVER',
            'priority': 'HIGH',
            'description': 'Nginx service is down and website is returning 502 bad gateway errors.'
        })
        self.assertEqual(inc_resp.status_code, 302)
        new_inc = Incident.objects.filter(title='Nginx server unavailable').first()
        self.assertIsNotNone(new_inc)

        # Switch to Admin
        client.login(username='admin', password='adminpassword')

        # Phase 4: Recommendation Check
        rec = RunbookRecommendation.objects.filter(incident=new_inc).first()
        self.assertIsNotNone(rec)

        # Phase 5: Request Approval
        req_resp = client.post(reverse('admin_incident_request_approval', kwargs={'pk': new_inc.pk}))
        self.assertEqual(req_resp.status_code, 302)
        approval = AutomationApproval.objects.filter(incident=new_inc).first()
        self.assertIsNotNone(approval)
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.PENDING)

        # Phase 5: Approve
        app_resp = client.post(reverse('approve_action', kwargs={'pk': approval.pk}), {'reason': 'Approved by admin'})
        self.assertEqual(app_resp.status_code, 302)
        approval.refresh_from_db()
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.APPROVED)

    # Code Safety Audit Test (Verify zero dangerous calls)
    def test_code_safety_audit(self):
        dangerous_tokens = ['os.system', 'subprocess.run', 'subprocess.Popen', 'shell=True', 'exec(', 'eval(']
        base_dir = str(settings.BASE_DIR)

        for root, dirs, files in os.walk(base_dir):
            if 'venv' in dirs:
                dirs.remove('venv')
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')

            for filename in files:
                if filename.endswith('.py') and not filename.startswith('test') and filename != 'tests.py':
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for token in dangerous_tokens:
                            self.assertNotIn(token, content, f"Dangerous token '{token}' detected in {filepath}!")

    # Backward compatibility tests
    def test_approved_execution(self):
        self.test_01_approved_approval_safe_action_success()

    def test_pending_approval_block(self):
        self.test_02_pending_approval_blocked()

    def test_rejected_approval_block(self):
        self.test_03_rejected_approval_blocked()

    def test_unknown_action_block(self):
        self.test_05_unknown_unsafe_action_blocked()

    def test_inactive_runbook_block(self):
        self.test_04_inactive_runbook_blocked()

    def test_duplicate_execution_prevention(self):
        self.test_10_duplicate_execution_blocked()

    def test_employee_security(self):
        self.test_06_employee_execution_denied()

    def test_csrf_protection_and_post_only(self):
        self.test_08_get_request_must_not_execute()

    def test_failed_action(self):
        self.test_11_simulation_function_failure()


class Phase7VerificationTests(TestCase):
    def setUp(self):
        # 1. Admin & Employee users
        self.admin_user = User.objects.create_user(username='admin_p7', password='adminpassword')
        self.admin_user.profile.role = Profile.Role.IT_ADMIN
        self.admin_user.profile.save()

        self.employee = User.objects.create_user(username='employee_p7', password='employeepassword')
        self.employee.profile.role = Profile.Role.EMPLOYEE
        self.employee.profile.save()

        # 2. Runbook
        self.runbook = Runbook.objects.create(
            title='Restart Nginx Web Server',
            category=Incident.Category.SERVER,
            description='Procedure for recovering Nginx.',
            symptoms='Nginx down',
            steps='Restart nginx',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='restart_nginx',
            created_by=self.admin_user,
            is_active=True
        )

        # 3. Incident
        self.incident = Incident.objects.create(
            title='Nginx server down',
            description='Nginx is not responding.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )

        # 3b. Recommendation
        self.recommendation = RunbookRecommendation.objects.create(
            incident=self.incident,
            runbook=self.runbook,
            match_score=0.95
        )

        # 4. Approval
        self.approval = AutomationApproval.objects.create(
            incident=self.incident,
            runbook=self.runbook,
            requested_by=self.admin_user,
            reviewed_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_at=timezone.now()
        )

        # 5. Successful Execution
        self.execution = AutomationExecution.objects.create(
            approval=self.approval,
            action_name='restart_nginx',
            status=AutomationExecution.ExecutionStatus.SUCCESS,
            output='Nginx restart simulated successfully.',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

    # TEST 1 — Successful execution verification
    def test_01_successful_execution_verification(self):
        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        verification = VerificationResult.objects.get(execution=self.execution)
        self.assertEqual(verification.status, VerificationResult.Status.PASSED)
        self.assertIn("Nginx service is responding normally", verification.message)

    # TEST 2 — Failed execution cannot be verified
    def test_02_failed_execution_cannot_be_verified(self):
        self.execution.status = AutomationExecution.ExecutionStatus.FAILED
        self.execution.save()

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertNotEqual(self.incident.status, Incident.Status.RESOLVED)
        self.assertFalse(VerificationResult.objects.filter(execution=self.execution, status=VerificationResult.Status.PASSED).exists())

    # TEST 3 — Blocked execution cannot be verified
    def test_03_blocked_execution_cannot_be_verified(self):
        self.execution.status = AutomationExecution.ExecutionStatus.BLOCKED
        self.execution.save()

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertNotEqual(self.incident.status, Incident.Status.RESOLVED)
        self.assertFalse(VerificationResult.objects.filter(execution=self.execution, status=VerificationResult.Status.PASSED).exists())

    # TEST 4 — Pending execution cannot be verified
    def test_04_pending_execution_cannot_be_verified(self):
        self.execution.status = AutomationExecution.ExecutionStatus.PENDING
        self.execution.save()

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertNotEqual(self.incident.status, Incident.Status.RESOLVED)

    # TEST 5 — Successful verification resolves incident
    def test_05_successful_verification_resolves_incident(self):
        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, Incident.Status.RESOLVED)
        self.assertIsNotNone(self.incident.resolved_at)

        # Timeline logged
        activity_logged = IncidentActivity.objects.filter(
            incident=self.incident,
            action='AUTOMATION_VERIFIED'
        ).exists()
        self.assertTrue(activity_logged)

    # TEST 6 — Failed verification does not resolve incident
    def test_06_failed_verification_does_not_resolve_incident(self):
        # Setup an execution with failing verification action
        failing_runbook = Runbook.objects.create(
            title='Check Service With Verification Failure',
            category=Incident.Category.SERVER,
            description='Procedure with failing verification.',
            symptoms='Failure',
            steps='Verify fail',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='simulate_verification_failure',
            created_by=self.admin_user,
            is_active=True
        )
        failing_incident = Incident.objects.create(
            title='Service problem',
            description='Problem needing verification.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )
        failing_approval = AutomationApproval.objects.create(
            incident=failing_incident,
            runbook=failing_runbook,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED
        )
        failing_execution = AutomationExecution.objects.create(
            approval=failing_approval,
            action_name='simulate_verification_failure',
            status=AutomationExecution.ExecutionStatus.SUCCESS,
            output='Execution succeeded.',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': failing_execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        failing_incident.refresh_from_db()
        self.assertNotEqual(failing_incident.status, Incident.Status.RESOLVED)
        self.assertEqual(failing_incident.status, Incident.Status.IN_PROGRESS)

        verification = VerificationResult.objects.get(execution=failing_execution)
        self.assertEqual(verification.status, VerificationResult.Status.FAILED)

    # TEST 7 — Employee cannot verify
    def test_07_employee_cannot_verify(self):
        client = Client()
        client.login(username='employee_p7', password='employeepassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)
        self.assertFalse(VerificationResult.objects.filter(execution=self.execution).exists())

    # TEST 8 — Anonymous user cannot verify
    def test_08_anonymous_user_cannot_verify(self):
        client = Client()
        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # TEST 9 — GET cannot verify
    def test_09_get_cannot_verify(self):
        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(VerificationResult.objects.filter(execution=self.execution).exists())

    # TEST 10 — Duplicate successful verification
    def test_10_duplicate_successful_verification(self):
        # Create initial PASSED verification
        VerificationResult.objects.create(
            execution=self.execution,
            status=VerificationResult.Status.PASSED,
            message="Initial verification pass."
        )

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        # Still only 1 record and message remains original
        self.assertEqual(VerificationResult.objects.filter(execution=self.execution).count(), 1)
        verification = VerificationResult.objects.get(execution=self.execution)
        self.assertEqual(verification.message, "Initial verification pass.")

    # TEST 11 — Missing execution
    def test_11_missing_execution(self):
        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': 999999})
        response = client.post(url)
        self.assertEqual(response.status_code, 404)

    # TEST 12 — Missing approval relationship
    def test_12_missing_approval(self):
        from automation.verification import verify_execution
        self.execution.approval = None
        is_passed, verif, msg = verify_execution(self.execution)
        self.assertFalse(is_passed)
        self.assertIn("approval", msg.lower())

    # TEST 13 — Inactive runbook
    def test_13_inactive_runbook(self):
        self.runbook.is_active = False
        self.runbook.save()

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertNotEqual(self.incident.status, Incident.Status.RESOLVED)

    # TEST 14 — Incident already resolved
    def test_14_incident_already_resolved(self):
        self.incident.status = Incident.Status.RESOLVED
        self.incident.save()

        from automation.verification import verify_execution
        is_passed, verif, msg = verify_execution(self.execution)
        self.assertFalse(is_passed)
        self.assertIn("already resolved", msg.lower())

    # TEST 15 — Verification result is stored
    def test_15_verification_result_is_stored(self):
        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        client.post(url)

        verif = VerificationResult.objects.filter(execution=self.execution).first()
        self.assertIsNotNone(verif)
        self.assertEqual(verif.execution, self.execution)
        self.assertEqual(verif.status, VerificationResult.Status.PASSED)
        self.assertTrue(len(verif.message) > 0)
        self.assertIsNotNone(verif.checked_at)

    # TEST 16 — Successful verification updates UI
    def test_16_successful_verification_updates_ui(self):
        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': self.execution.pk})
        client.post(url)

        # View approval detail
        detail_resp = client.get(reverse('approval_detail', kwargs={'pk': self.approval.pk}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "PASSED")
        self.assertContains(detail_resp, "Verification Passed")

        # View incident detail
        inc_resp = client.get(reverse('admin_incident_detail', kwargs={'pk': self.incident.pk}))
        self.assertEqual(inc_resp.status_code, 200)
        self.assertContains(inc_resp, "RESOLVED")
        self.assertContains(inc_resp, "PASSED")

    # TEST 17 — Failed verification updates UI
    def test_17_failed_verification_updates_ui(self):
        failing_runbook = Runbook.objects.create(
            title='Check Service UI Failure',
            category=Incident.Category.SERVER,
            description='UI check failure.',
            symptoms='Fail',
            steps='Fail',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='simulate_verification_failure',
            created_by=self.admin_user,
            is_active=True
        )
        failing_incident = Incident.objects.create(
            title='Service UI Failure Incident',
            description='Problem description.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )
        RunbookRecommendation.objects.create(
            incident=failing_incident,
            runbook=failing_runbook,
            match_score=0.95
        )
        failing_approval = AutomationApproval.objects.create(
            incident=failing_incident,
            runbook=failing_runbook,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED
        )
        failing_execution = AutomationExecution.objects.create(
            approval=failing_approval,
            action_name='simulate_verification_failure',
            status=AutomationExecution.ExecutionStatus.SUCCESS,
            output='Execution completed.',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        client = Client()
        client.login(username='admin_p7', password='adminpassword')

        url = reverse('admin_execution_verify', kwargs={'pk': failing_execution.pk})
        client.post(url)

        # View approval detail
        detail_resp = client.get(reverse('approval_detail', kwargs={'pk': failing_approval.pk}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "FAILED")
        self.assertContains(detail_resp, "verification failed")

        # View incident detail
        inc_resp = client.get(reverse('admin_incident_detail', kwargs={'pk': failing_incident.pk}))
        self.assertEqual(inc_resp.status_code, 200)
        self.assertContains(inc_resp, "FAILED")
        self.assertNotEqual(failing_incident.status, Incident.Status.RESOLVED)


