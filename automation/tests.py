from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from accounts.models import Profile
from incidents.models import Incident, IncidentActivity
from runbooks.models import Runbook, RunbookRecommendation
from automation.models import AutomationApproval, AutomationExecution
from automation.actions import SAFE_ACTIONS

User = get_user_model()

class Phase6SafeAutomationTests(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_user.profile.role = Profile.Role.IT_ADMIN
        self.admin_user.profile.save()

        self.employee = User.objects.create_user(username='employee', password='employeepassword')
        self.employee.profile.role = Profile.Role.EMPLOYEE
        self.employee.profile.save()

        # Seed an active, allowlisted runbook
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

        # Seed a runbook with an unknown action
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

        # Create Incidents
        self.incident = Incident.objects.create(
            title='Nginx Service Down',
            description='Nginx is down.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee,
            status=Incident.Status.APPROVED
        )

        # Recommendation
        self.recommendation = RunbookRecommendation.objects.create(
            incident=self.incident,
            runbook=self.runbook,
            match_score=0.9
        )

        # Approval
        self.approval = AutomationApproval.objects.create(
            incident=self.incident,
            runbook=self.runbook,
            requested_by=self.admin_user,
            reviewed_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_at=timezone.now()
        )

    def test_approved_execution(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Trigger execution via POST
        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify execution is created and is SUCCESSful
        execution = AutomationExecution.objects.get(approval=self.approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.SUCCESS)
        self.assertEqual(execution.action_name, 'restart_nginx')
        self.assertEqual(execution.output, 'Nginx restart simulated successfully.')
        self.assertIsNotNone(execution.started_at)
        self.assertIsNotNone(execution.completed_at)

        # Verify Incident status is NOT resolved (keep it APPROVED or IN_PROGRESS)
        self.incident.refresh_from_db()
        self.assertNotEqual(self.incident.status, Incident.Status.RESOLVED)

        # Verify Incident Activity timeline
        activity_start = IncidentActivity.objects.filter(
            incident=self.incident,
            action='AUTOMATION_STARTED',
            description__contains='Approved automation action started: restart_nginx.'
        ).exists()
        activity_success = IncidentActivity.objects.filter(
            incident=self.incident,
            action='AUTOMATION_SUCCESS',
            description__contains='Automation action completed successfully: restart_nginx.'
        ).exists()
        self.assertTrue(activity_start)
        self.assertTrue(activity_success)

    def test_pending_approval_block(self):
        # Create pending approval
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

        # Execution should exist and be BLOCKED
        execution = AutomationExecution.objects.get(approval=pending_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Approval status must be APPROVED.")

        # Timeline logged
        activity_blocked = IncidentActivity.objects.filter(
            incident=pending_incident,
            action='AUTOMATION_BLOCKED',
            description__contains='Automation action blocked by safety validation.'
        ).exists()
        self.assertTrue(activity_blocked)

    def test_rejected_approval_block(self):
        # Create rejected approval
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

        # Execution should be BLOCKED
        execution = AutomationExecution.objects.get(approval=rejected_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Approval status must be APPROVED.")

    def test_unknown_action_block(self):
        # Create approval with runbook having unallowlisted action
        unknown_incident = Incident.objects.create(
            title='Unknown Action Incident',
            description='Dangerous action.',
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

        # Execution should be BLOCKED
        execution = AutomationExecution.objects.get(approval=unknown_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Action is not present in the approved automation allowlist.")

    def test_inactive_runbook_block(self):
        # Deactivate runbook
        self.runbook.is_active = False
        self.runbook.save()

        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        # Execution should be BLOCKED
        execution = AutomationExecution.objects.get(approval=self.approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.BLOCKED)
        self.assertEqual(execution.error_message, "Runbook is no longer active.")

        # Reactivate
        self.runbook.is_active = True
        self.runbook.save()

    def test_duplicate_execution_prevention(self):
        # Mark as successful first
        AutomationExecution.objects.create(
            approval=self.approval,
            action_name='restart_nginx',
            status=AutomationExecution.ExecutionStatus.SUCCESS,
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        client = Client()
        client.login(username='admin', password='adminpassword')

        # Trigger execution again
        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        self.assertEqual(response.status_code, 302)

        # Ensure only 1 execution record exists
        self.assertEqual(AutomationExecution.objects.filter(approval=self.approval).count(), 1)

    def test_employee_security(self):
        client = Client()
        client.login(username='employee', password='employeepassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        response = client.post(url)
        # Should redirect to employee dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

    def test_csrf_protection_and_post_only(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        url = reverse('admin_approval_execute', kwargs={'pk': self.approval.pk})
        # GET request should return HTTP 405 (Method Not Allowed)
        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_failed_action(self):
        # Runbook with failing action
        failing_runbook = Runbook.objects.create(
            title='Failing Runbook',
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
            title='Failing Action Incident',
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

        # Verify execution is created and is FAILED
        execution = AutomationExecution.objects.get(approval=failing_approval)
        self.assertEqual(execution.status, AutomationExecution.ExecutionStatus.FAILED)
        self.assertEqual(execution.error_message, "Simulation failed: Simulated action failure.")
        self.assertIsNotNone(execution.completed_at)

        # Incident status is not resolved
        failing_incident.refresh_from_db()
        self.assertNotEqual(failing_incident.status, Incident.Status.RESOLVED)

        # Timeline logged
        activity_failed = IncidentActivity.objects.filter(
            incident=failing_incident,
            action='AUTOMATION_FAILED',
            description__contains='Automation action failed: simulate_failure.'
        ).exists()
        self.assertTrue(activity_failed)
