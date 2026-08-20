from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from accounts.models import Profile
from incidents.models import Incident, IncidentActivity
from runbooks.models import Runbook, RunbookRecommendation
from automation.models import AutomationApproval

User = get_user_model()

class Phase4ComprehensiveTestSuite(TestCase):
    def setUp(self):
        # 1. Create users and update their automatically generated profiles
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword')
        self.admin_user.profile.role = Profile.Role.IT_ADMIN
        self.admin_user.profile.save()

        self.employee1 = User.objects.create_user(username='emp1', password='emppassword')
        self.employee1.profile.role = Profile.Role.EMPLOYEE
        self.employee1.profile.save()

        self.employee2 = User.objects.create_user(username='emp2', password='emppassword')
        self.employee2.profile.role = Profile.Role.EMPLOYEE
        self.employee2.profile.save()

        # 2. Seed Runbooks (at least 10 active runbooks)
        self.nginx_rb = Runbook.objects.create(
            title='Restart Nginx Web Server',
            category=Incident.Category.SERVER,
            description='Procedure for recovering an Nginx web server when the service is unavailable or not responding.',
            symptoms='Website unavailable\nNginx service inactive\nConnection refused\nHTTP 502/503 errors',
            steps='1. Check Nginx service status.\n2. Review Nginx error logs.\n3. Validate Nginx configuration.\n4. Restart Nginx.',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='restart_nginx',
            created_by=self.admin_user
        )

        self.postgres_rb = Runbook.objects.create(
            title='PostgreSQL Connection Recovery',
            category=Incident.Category.DATABASE,
            description='Troubleshooting procedure for applications that cannot connect to a PostgreSQL database.',
            symptoms='Database connection refused\nConnection timeout\nPostgreSQL service inactive\nApplication database errors',
            steps='1. Check PostgreSQL service status.\n2. Verify database host and port.\n3. Check PostgreSQL logs.',
            risk_level=Runbook.RiskLevel.HIGH,
            automation_action='restart_postgresql',
            created_by=self.admin_user
        )

        self.disk_rb = Runbook.objects.create(
            title='Clear Disk Space',
            category=Incident.Category.STORAGE,
            description='Procedure for investigating low disk space and safely identifying removable temporary files.',
            symptoms='Disk usage above threshold\nLow storage warning\nApplication unable to write files\nLog storage growing rapidly',
            steps='1. Check disk usage.\n2. Identify large directories.\n3. Clear temp files.',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='check_disk_space',
            created_by=self.admin_user
        )

        self.apache_rb = Runbook.objects.create(
            title='Restart Apache Web Server',
            category=Incident.Category.SERVER,
            description='Procedure for recovering an Apache web server.',
            symptoms='Website unavailable\nConnection refused\nApache service inactive',
            steps='1. Restart Apache.',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='restart_apache',
            created_by=self.admin_user
        )

        self.mysql_rb = Runbook.objects.create(
            title='MySQL Service Recovery',
            category=Incident.Category.DATABASE,
            description='Procedure for MySQL service recovery.',
            symptoms='MySQL connection refused\nDatabase unavailable',
            steps='1. Restart MySQL.',
            risk_level=Runbook.RiskLevel.HIGH,
            automation_action='restart_mysql',
            created_by=self.admin_user
        )

        self.network_rb = Runbook.objects.create(
            title='Network Connectivity Troubleshooting',
            category=Incident.Category.NETWORK,
            description='Procedure for network connectivity problems.',
            symptoms='Cannot reach internal service\nHigh latency\nPacket loss',
            steps='1. Check local network.',
            risk_level=Runbook.RiskLevel.LOW,
            automation_action='check_network',
            created_by=self.admin_user
        )

        self.dns_rb = Runbook.objects.create(
            title='DNS Resolution Troubleshooting',
            category=Incident.Category.NETWORK,
            description='Procedure for DNS resolution troubleshooting.',
            symptoms='Domain cannot be resolved\nDNS timeout',
            steps='1. Check DNS config.',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='check_dns',
            created_by=self.admin_user
        )

        self.app_rb = Runbook.objects.create(
            title='Application Service Restart',
            category=Incident.Category.APPLICATION,
            description='Procedure for application service restart.',
            symptoms='Application unavailable\nRequest timeout',
            steps='1. Restart app.',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='restart_application',
            created_by=self.admin_user
        )

        self.cache_rb = Runbook.objects.create(
            title='Clear Application Cache',
            category=Incident.Category.APPLICATION,
            description='Procedure for clearing application cache.',
            symptoms='Stale application data\nUnexpected cached response',
            steps='1. Clear cache.',
            risk_level=Runbook.RiskLevel.LOW,
            automation_action='clear_application_cache',
            created_by=self.admin_user
        )

        self.ssl_rb = Runbook.objects.create(
            title='SSL Certificate Expiry Check',
            category=Incident.Category.SECURITY,
            description='Procedure for SSL certificate check.',
            symptoms='Browser certificate warning\nHTTPS connection error',
            steps='1. Check certificate date.',
            risk_level=Runbook.RiskLevel.MEDIUM,
            automation_action='check_ssl_certificate',
            created_by=self.admin_user
        )

    # 4. Phase 1 Regression Test
    def test_phase1_regression(self):
        client = Client()

        # Login Employee
        login_success = client.login(username='emp1', password='emppassword')
        self.assertTrue(login_success)

        # Employee Dashboard Access
        response = client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Employee cannot access Admin Dashboard
        response = client.get(reverse('admin_dashboard'))
        # Should redirect to employee dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

        # Logout Employee
        response = client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        # Login Admin
        login_success = client.login(username='admin', password='adminpassword')
        self.assertTrue(login_success)

        # Admin Dashboard Access
        response = client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Admin cannot access Employee Dashboard
        response = client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_dashboard'), response.url)

    # 5. Phase 2 Regression Test
    def test_phase2_regression(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create new incident
        response = client.post(reverse('employee_incident_create'), {
            'title': 'Test Incident',
            'description': 'A test incident description for checking sequential numbers.',
            'category': 'NETWORK',
            'priority': 'MEDIUM'
        })
        self.assertEqual(response.status_code, 302)

        # Verify saved incident
        inc = Incident.objects.get(title='Test Incident')
        self.assertEqual(inc.created_by, self.employee1)
        self.assertTrue(inc.incident_number.startswith('INC-'))

        # Employee sees own incident
        response = client.get(reverse('employee_incident_detail', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 200)

        # Verify employee cannot see another employee's incident
        client.logout()
        client.login(username='emp2', password='emppassword')
        response = client.get(reverse('employee_incident_detail', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 404)

        # Admin sees the incident
        client.logout()
        client.login(username='admin', password='adminpassword')
        response = client.get(reverse('admin_incident_detail', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 200)

        # Admin changes priority and status
        response = client.post(reverse('admin_incident_update', kwargs={'pk': inc.pk}), {
            'priority': 'HIGH',
            'status': 'IN_PROGRESS'
        })
        self.assertEqual(response.status_code, 302)

        inc.refresh_from_db()
        self.assertEqual(inc.priority, 'HIGH')
        self.assertEqual(inc.status, 'IN_PROGRESS')

        # Activity timeline updates
        activities = IncidentActivity.objects.filter(incident=inc)
        self.assertTrue(activities.exists())

    # 6. Phase 3 Regression Test
    def test_phase3_regression(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Runbook list
        response = client.get(reverse('runbook_list'))
        self.assertEqual(response.status_code, 200)

        # Create Runbook
        response = client.post(reverse('runbook_create'), {
            'title': 'New Runbook Test',
            'category': 'SERVER',
            'description': 'Description for new runbook.',
            'symptoms': 'Symptom test',
            'steps': 'Step test',
            'risk_level': 'LOW',
            'automation_action': 'test_action',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        new_rb = Runbook.objects.get(title='New Runbook Test')
        self.assertTrue(new_rb.runbook_number.startswith('RB-'))

        # Edit Runbook
        response = client.post(reverse('runbook_edit', kwargs={'pk': new_rb.pk}), {
            'title': 'New Runbook Test Edited',
            'category': 'SERVER',
            'description': 'Description for new runbook.',
            'symptoms': 'Symptom test',
            'steps': 'Step test',
            'risk_level': 'LOW',
            'automation_action': 'test_action',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        new_rb.refresh_from_db()
        self.assertEqual(new_rb.title, 'New Runbook Test Edited')

        # Deactivate / Activate Runbook
        self.assertTrue(new_rb.is_active)
        # Deactivate
        response = client.post(reverse('runbook_toggle_active', kwargs={'pk': new_rb.pk}))
        self.assertEqual(response.status_code, 302)
        new_rb.refresh_from_db()
        self.assertFalse(new_rb.is_active)

        # Activate
        response = client.post(reverse('runbook_toggle_active', kwargs={'pk': new_rb.pk}))
        self.assertEqual(response.status_code, 302)
        new_rb.refresh_from_db()
        self.assertTrue(new_rb.is_active)

        # Search/Filters works
        response = client.get(reverse('runbook_list') + '?search=Apache')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apache')

        response = client.get(reverse('runbook_list') + '?category=SERVER')
        self.assertEqual(response.status_code, 200)

        # At least 10 runbooks exist
        self.assertGreaterEqual(Runbook.objects.count(), 10)

    # 7. AI Test - NGINX
    def test_ai_nginx(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create Website is slow incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Website is slow',
            'description': 'Users are getting Nginx 502 connection refused errors when accessing the dashboard. The Nginx web server may have stopped responding.',
            'category': 'SERVER',
            'priority': 'HIGH'
        })

        inc = Incident.objects.get(title='Website is slow')
        recommendation = RunbookRecommendation.objects.get(incident=inc)
        self.assertEqual(recommendation.runbook, self.nginx_rb)

    # 8. AI Test - DATABASE
    def test_ai_database(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create Database connection failure incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Database connection failure',
            'description': 'The application cannot connect to PostgreSQL. Users are receiving connection refused errors and the PostgreSQL database service may not be responding.',
            'category': 'DATABASE',
            'priority': 'CRITICAL'
        })

        inc = Incident.objects.get(title='Database connection failure')
        recommendation = RunbookRecommendation.objects.get(incident=inc)
        self.assertEqual(recommendation.runbook, self.postgres_rb)

    # 9. AI Test - STORAGE
    def test_ai_storage(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create Server disk almost full incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Server disk almost full',
            'description': 'The production server is running out of disk space. Application logs have grown significantly and the system is reporting low storage warnings.',
            'category': 'STORAGE',
            'priority': 'MEDIUM'
        })

        inc = Incident.objects.get(title='Server disk almost full')
        recommendation = RunbookRecommendation.objects.get(incident=inc)
        self.assertEqual(recommendation.runbook, self.disk_rb)

    # 10. NO-MATCH TEST
    def test_no_match(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create Office chair broken incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Office chair broken',
            'description': 'The chair in the meeting room is damaged and needs replacement.',
            'category': 'OTHER',
            'priority': 'LOW'
        })

        inc = Incident.objects.get(title='Office chair broken')
        # Expect no recommendation saved
        rec_exists = RunbookRecommendation.objects.filter(incident=inc).exists()
        self.assertFalse(rec_exists)
        self.assertEqual(inc.status, Incident.Status.OPEN)

    # 11. INACTIVE RUNBOOK TEST
    def test_inactive_runbook(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Deactivate Nginx Web Server runbook
        self.nginx_rb.is_active = False
        self.nginx_rb.save()

        # Create Nginx 502 connection refused incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Nginx 502 connection refused',
            'description': 'Users are getting Nginx 502 connection refused errors when accessing the dashboard. The Nginx web server may have stopped responding.',
            'category': 'SERVER',
            'priority': 'HIGH'
        })

        inc = Incident.objects.get(title='Nginx 502 connection refused')
        rec = RunbookRecommendation.objects.filter(incident=inc).first()
        if rec:
            self.assertNotEqual(rec.runbook, self.nginx_rb)

        # Reactivate Nginx
        self.nginx_rb.is_active = True
        self.nginx_rb.save()

    # 12. SCORE TEST
    def test_score_storage(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create Website is slow incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Website is slow',
            'description': 'Users are getting Nginx 502 connection refused errors when accessing the dashboard. The Nginx web server may have stopped responding.',
            'category': 'SERVER',
            'priority': 'HIGH'
        })

        inc = Incident.objects.get(title='Website is slow')
        recommendation = RunbookRecommendation.objects.get(incident=inc)
        score = recommendation.match_score
        
        # Verify 0 <= score <= 1
        self.assertTrue(0.0 <= score <= 1.0)
        
        # Check that it's the raw similarity score and not multiplied by 100
        # (A score of 91.43 is way outside [0, 1] range)
        self.assertLessEqual(score, 1.0)

    # 13. DUPLICATE TEST
    def test_duplicate_prevention(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create incident
        client.post(reverse('employee_incident_create'), {
            'title': 'Website is slow',
            'description': 'Users are getting Nginx 502 connection refused errors when accessing the dashboard.',
            'category': 'SERVER',
            'priority': 'HIGH'
        })

        inc = Incident.objects.get(title='Website is slow')
        
        # Open details page 5 times
        for _ in range(5):
            client.get(reverse('employee_incident_detail', kwargs={'pk': inc.pk}))

        # Ensure only 1 recommendation exists
        recs = RunbookRecommendation.objects.filter(incident=inc)
        self.assertEqual(recs.count(), 1)

    # 14. ANALYZE AGAIN TEST
    def test_analyze_again(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Create incident
        inc = Incident.objects.create(
            title='Website is slow',
            description='Users are getting Nginx 502 connection refused errors when accessing the dashboard. The Nginx web server may have stopped responding.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee1
        )

        # Trigger initial retrieval manually
        from runbooks.retrieval import retrieve_best_runbook
        res = retrieve_best_runbook(inc)
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=res['runbook'],
            match_score=res['score']
        )

        initial_timeline_count = IncidentActivity.objects.filter(incident=inc).count()

        # Trigger Analyze Again via POST
        response = client.post(reverse('admin_incident_analyze', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 302)

        # Verify only one recommendation exists, updated
        recs = RunbookRecommendation.objects.filter(incident=inc)
        self.assertEqual(recs.count(), 1)
        self.assertEqual(recs.first().runbook, self.nginx_rb)

        # Activity timeline records the re-analysis
        new_timeline_count = IncidentActivity.objects.filter(incident=inc).count()
        self.assertGreater(new_timeline_count, initial_timeline_count)

    # 15. EMPLOYEE SECURITY TEST
    def test_employee_security_analyze_endpoint(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Create incident
        inc = Incident.objects.create(
            title='Website is slow',
            description='Users are getting Nginx 502 connection refused errors when accessing the dashboard.',
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            created_by=self.employee1
        )

        # Try to POST to analyze endpoint as employee
        response = client.post(reverse('admin_incident_analyze', kwargs={'pk': inc.pk}))
        # Redirected because of it_admin_required decorator
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

    # 16. FAILURE TEST
    def test_all_runbooks_inactive_failure(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        # Temporarily deactivate all runbooks
        Runbook.objects.all().update(is_active=False)

        # Create incident (website should not crash)
        response = client.post(reverse('employee_incident_create'), {
            'title': 'Nginx 502 connection refused',
            'description': 'Users are getting Nginx 502 connection refused errors when accessing the dashboard.',
            'category': 'SERVER',
            'priority': 'HIGH'
        })
        self.assertEqual(response.status_code, 302)

        inc = Incident.objects.get(title='Nginx 502 connection refused', status=Incident.Status.OPEN)
        self.assertFalse(RunbookRecommendation.objects.filter(incident=inc).exists())

        # Reactivate runbooks
        Runbook.objects.all().update(is_active=True)

    # ============================================================
    # PHASE 5 TESTS
    # ============================================================

    def test_phase5_request_approval(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Create incident
        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='The application cannot connect to PostgreSQL. Users are receiving connection refused errors.',
            category=Incident.Category.DATABASE,
            priority=Incident.Priority.HIGH,
            created_by=self.employee1
        )
        # Create recommendation
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        inc.status = Incident.Status.RECOMMENDATION_READY
        inc.save()

        # POST to request-approval
        response = client.post(reverse('admin_incident_request_approval', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 302)

        # Verify AutomationApproval created
        approval = AutomationApproval.objects.get(incident=inc)
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.PENDING)
        self.assertEqual(approval.runbook, self.postgres_rb)
        self.assertEqual(approval.requested_by, self.admin_user)

        # Verify incident status changed to PENDING_APPROVAL
        inc.refresh_from_db()
        self.assertEqual(inc.status, Incident.Status.PENDING_APPROVAL)

        # Verify activity timeline entry
        activity_exists = IncidentActivity.objects.filter(
            incident=inc,
            action='APPROVAL_REQUESTED',
            description__contains="Approval requested by admin for RB-0002 — PostgreSQL Connection Recovery."
        ).exists()
        self.assertTrue(activity_exists)

    def test_phase5_duplicate_approval(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Create incident
        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        # Create recommendation
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        inc.status = Incident.Status.RECOMMENDATION_READY
        inc.save()

        # Request first approval
        client.post(reverse('admin_incident_request_approval', kwargs={'pk': inc.pk}))
        self.assertEqual(AutomationApproval.objects.filter(incident=inc).count(), 1)

        # Request second approval (must not create duplicate)
        response = client.post(reverse('admin_incident_request_approval', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AutomationApproval.objects.filter(incident=inc).count(), 1)

    def test_phase5_approve(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.PENDING
        )
        inc.status = Incident.Status.PENDING_APPROVAL
        inc.save()

        # Approve action POST
        response = client.post(reverse('approve_action', kwargs={'pk': approval.pk}), {
            'reason': 'Approved for test environment recovery.'
        })
        self.assertEqual(response.status_code, 302)

        approval.refresh_from_db()
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.APPROVED)
        self.assertEqual(approval.reviewed_by, self.admin_user)
        self.assertIsNotNone(approval.reviewed_at)
        self.assertEqual(approval.reason, 'Approved for test environment recovery.')

        # Verify incident status updated to APPROVED
        inc.refresh_from_db()
        self.assertEqual(inc.status, Incident.Status.APPROVED)

        # Verify activity timeline entry
        activity_exists = IncidentActivity.objects.filter(
            incident=inc,
            action='APPROVAL_APPROVED',
            description__contains="Automation action approved by admin for RB-0002 — PostgreSQL Connection Recovery."
        ).exists()
        self.assertTrue(activity_exists)

    def test_phase5_reject(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.PENDING
        )
        inc.status = Incident.Status.PENDING_APPROVAL
        inc.save()

        # Reject action POST
        response = client.post(reverse('reject_action', kwargs={'pk': approval.pk}), {
            'reason': 'Runbook does not match the current environment.'
        })
        self.assertEqual(response.status_code, 302)

        approval.refresh_from_db()
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.REJECTED)
        self.assertEqual(approval.reviewed_by, self.admin_user)
        self.assertIsNotNone(approval.reviewed_at)
        self.assertEqual(approval.reason, 'Runbook does not match the current environment.')

        # Verify incident status updated to REJECTED
        inc.refresh_from_db()
        self.assertEqual(inc.status, Incident.Status.REJECTED)

        # Verify activity timeline entry
        activity_exists = IncidentActivity.objects.filter(
            incident=inc,
            action='APPROVAL_REJECTED',
            description__contains="Automation action rejected by admin. Reason: Runbook does not match the current environment."
        ).exists()
        self.assertTrue(activity_exists)

    def test_phase5_empty_rejection(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.PENDING
        )

        # Reject action POST with empty reason
        response = client.post(reverse('reject_action', kwargs={'pk': approval.pk}), {
            'reason': ''
        })
        self.assertEqual(response.status_code, 302)
        approval.refresh_from_db()
        # Verify approval remains PENDING
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.PENDING)

    def test_phase5_employee_security(self):
        client = Client()
        client.login(username='emp1', password='emppassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.PENDING
        )

        # Try accessing approvals list
        response = client.get(reverse('approval_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

        # Try accessing approval detail
        response = client.get(reverse('approval_detail', kwargs={'pk': approval.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

        # Try POST to approve endpoint
        response = client.post(reverse('approve_action', kwargs={'pk': approval.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('employee_dashboard'), response.url)

    def test_phase5_inactive_runbook(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        # Deactivate postgres_rb
        self.postgres_rb.is_active = False
        self.postgres_rb.save()

        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        inc.status = Incident.Status.RECOMMENDATION_READY
        inc.save()

        # Try Request Approval
        response = client.post(reverse('admin_incident_request_approval', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 302)

        # Verify no AutomationApproval created
        self.assertFalse(AutomationApproval.objects.filter(incident=inc).exists())

        # Reactivate runbook for other tests
        self.postgres_rb.is_active = True
        self.postgres_rb.save()

    def test_phase5_no_recommendation(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='Office chair broken',
            description='Unrelated description',
            category=Incident.Category.OTHER,
            created_by=self.employee1
        )
        # No recommendation created

        # Try Request Approval
        response = client.post(reverse('admin_incident_request_approval', kwargs={'pk': inc.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AutomationApproval.objects.filter(incident=inc).exists())

    def test_phase5_approve_twice(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.APPROVED,
            reviewed_by=self.admin_user,
            reviewed_at=timezone.now()
        )

        # Try approving again
        response = client.post(reverse('approve_action', kwargs={'pk': approval.pk}))
        self.assertEqual(response.status_code, 302)
        approval.refresh_from_db()
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.APPROVED)

    def test_phase5_reject_then_approve(self):
        client = Client()
        client.login(username='admin', password='adminpassword')

        inc = Incident.objects.create(
            title='PostgreSQL connection failure',
            description='Database connection issue',
            category=Incident.Category.DATABASE,
            created_by=self.employee1
        )
        rec = RunbookRecommendation.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            match_score=0.95
        )
        approval = AutomationApproval.objects.create(
            incident=inc,
            runbook=self.postgres_rb,
            requested_by=self.admin_user,
            status=AutomationApproval.ApprovalStatus.REJECTED,
            reviewed_by=self.admin_user,
            reviewed_at=timezone.now(),
            reason='Incorrect runbook match.'
        )

        # Try approving now
        response = client.post(reverse('approve_action', kwargs={'pk': approval.pk}))
        self.assertEqual(response.status_code, 302)
        approval.refresh_from_db()
        # Verify status remains REJECTED
        self.assertEqual(approval.status, AutomationApproval.ApprovalStatus.REJECTED)
