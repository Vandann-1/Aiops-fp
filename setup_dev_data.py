import os
import django

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiops_service_desk.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile
from incidents.models import Incident, IncidentActivity
from runbooks.models import Runbook

User = get_user_model()

def run():
    print("=" * 60)
    print(" Seeding Development Users & Incidents for AIOps Service Desk")
    print("=" * 60)
    
    # 1. Create Superuser / IT Admin
    admin_username = 'admin'
    admin_password = 'admin1234'
    if not User.objects.filter(username=admin_username).exists():
        admin = User.objects.create_superuser(
            username=admin_username,
            email='admin@aiops.local',
            password=admin_password
        )
        # Get or create profile, set role to IT_ADMIN
        profile, _ = Profile.objects.get_or_create(user=admin)
        profile.role = Profile.Role.IT_ADMIN
        profile.save()
        print(f"   [SUCCESS] IT Admin (Superuser) created: {admin_username}")
    else:
        admin = User.objects.get(username=admin_username)
        profile, _ = Profile.objects.get_or_create(user=admin)
        profile.role = Profile.Role.IT_ADMIN
        profile.save()
        print(f"   [INFO] Superuser '{admin_username}' verified.")

    # 2. Create Employee user
    employee_username = 'employee'
    employee_password = 'employee1234'
    if not User.objects.filter(username=employee_username).exists():
        employee = User.objects.create_user(
            username=employee_username,
            email='employee@aiops.local',
            password=employee_password
        )
        print(f"   [SUCCESS] Employee user created: {employee_username}")
    else:
        employee = User.objects.get(username=employee_username)
        print(f"   [INFO] Employee user '{employee_username}' already exists.")

    print("-" * 60)
    print(" Seeding Sample Incidents...")
    print("-" * 60)

    # 3. Create Sample Incident 1
    inc1_title = "Apache Server Not Responding"
    if not Incident.objects.filter(title=inc1_title).exists():
        inc1 = Incident.objects.create(
            title=inc1_title,
            category=Incident.Category.SERVER,
            priority=Incident.Priority.HIGH,
            description="Production website is unavailable. Users receive a connection error and Apache appears to have stopped responding.",
            created_by=employee,
            status=Incident.Status.OPEN
        )
        IncidentActivity.objects.create(
            incident=inc1,
            actor=employee,
            action='INCIDENT_CREATED',
            description=f"Incident reported by {employee.username}."
        )
        print(f"   [SUCCESS] Incident 1 created: {inc1.incident_number}")
    else:
        print(f"   [INFO] Incident 1 '{inc1_title}' already exists.")

    # 4. Create Sample Incident 2
    inc2_title = "Database Connection Failure"
    if not Incident.objects.filter(title=inc2_title).exists():
        inc2 = Incident.objects.create(
            title=inc2_title,
            category=Incident.Category.DATABASE,
            priority=Incident.Priority.CRITICAL,
            description="The application cannot connect to the database. Multiple users receive database connection errors when opening the application.",
            created_by=employee,
            status=Incident.Status.OPEN
        )
        IncidentActivity.objects.create(
            incident=inc2,
            actor=employee,
            action='INCIDENT_CREATED',
            description=f"Incident reported by {employee.username}."
        )
        print(f"   [SUCCESS] Incident 2 created: {inc2.incident_number}")
    else:
        print(f"   [INFO] Incident 2 '{inc2_title}' already exists.")

    # 5. Create Sample Incident 3
    inc3_title = "Office Network Extremely Slow"
    if not Incident.objects.filter(title=inc3_title).exists():
        inc3 = Incident.objects.create(
            title=inc3_title,
            category=Incident.Category.NETWORK,
            priority=Incident.Priority.MEDIUM,
            description="Multiple employees are experiencing very slow network connectivity and internal services take a long time to load.",
            created_by=employee,
            status=Incident.Status.OPEN
        )
        IncidentActivity.objects.create(
            incident=inc3,
            actor=employee,
            action='INCIDENT_CREATED',
            description=f"Incident reported by {employee.username}."
        )
        print(f"   [SUCCESS] Incident 3 created: {inc3.incident_number}")
    else:
        print(f"   [INFO] Incident 3 '{inc3_title}' already exists.")

    # 6. Seed Runbooks
    print("-" * 60)
    print(" Seeding Sample Runbooks...")
    print("-" * 60)
    
    runbooks_data = [
        {
            'title': 'Restart Apache Web Server',
            'category': 'SERVER',
            'description': 'Procedure for recovering an Apache web server that has stopped responding or become unavailable.',
            'symptoms': 'Website unavailable\nConnection refused\nApache service inactive\nHTTP 503 errors',
            'steps': '1. Check Apache service status.\n2. Review Apache error logs.\n3. Validate Apache configuration.\n4. Restart Apache.\n5. Verify Apache service status.\n6. Send a test HTTP request.\n7. Confirm website availability.',
            'risk_level': 'MEDIUM',
            'automation_action': 'restart_apache'
        },
        {
            'title': 'Restart Nginx Web Server',
            'category': 'SERVER',
            'description': 'Procedure for recovering an Nginx web server when the service is unavailable or not responding.',
            'symptoms': 'Website unavailable\nNginx service inactive\nConnection refused\nHTTP 502/503 errors',
            'steps': '1. Check Nginx service status.\n2. Review Nginx error logs.\n3. Validate Nginx configuration.\n4. Restart Nginx.\n5. Verify service status.\n6. Test the application endpoint.',
            'risk_level': 'MEDIUM',
            'automation_action': 'restart_nginx'
        },
        {
            'title': 'PostgreSQL Connection Recovery',
            'category': 'DATABASE',
            'description': 'Troubleshooting procedure for applications that cannot connect to a PostgreSQL database.',
            'symptoms': 'Database connection refused\nConnection timeout\nPostgreSQL service inactive\nApplication database errors',
            'steps': '1. Check PostgreSQL service status.\n2. Verify database host and port.\n3. Check PostgreSQL logs.\n4. Verify database connectivity.\n5. Confirm the application connection settings.\n6. Test the application again.',
            'risk_level': 'HIGH',
            'automation_action': 'restart_postgresql'
        },
        {
            'title': 'MySQL Service Recovery',
            'category': 'DATABASE',
            'description': 'Procedure for investigating and recovering a MySQL service that is unavailable.',
            'symptoms': 'MySQL connection refused\nDatabase unavailable\nMySQL service inactive\nApplication database errors',
            'steps': '1. Check MySQL service status.\n2. Review MySQL error logs.\n3. Check available disk space.\n4. Restart MySQL if appropriate.\n5. Verify database connectivity.\n6. Test the application.',
            'risk_level': 'HIGH',
            'automation_action': 'restart_mysql'
        },
        {
            'title': 'Clear Disk Space',
            'category': 'STORAGE',
            'description': 'Procedure for investigating low disk space and safely identifying removable temporary files.',
            'symptoms': 'Disk usage above threshold\nLow storage warning\nApplication unable to write files\nLog storage growing rapidly',
            'steps': '1. Check disk usage.\n2. Identify large directories.\n3. Identify old temporary files and logs.\n4. Verify files are safe to remove.\n5. Clean approved temporary data.\n6. Recheck disk usage.',
            'risk_level': 'MEDIUM',
            'automation_action': 'check_disk_space'
        },
        {
            'title': 'Network Connectivity Troubleshooting',
            'category': 'NETWORK',
            'description': 'Procedure for diagnosing basic network connectivity problems between a workstation and internal services.',
            'symptoms': 'Cannot reach internal service\nHigh latency\nPacket loss\nNetwork timeout',
            'steps': '1. Check local network connection.\n2. Test gateway connectivity.\n3. Test DNS resolution.\n4. Test the target service.\n5. Check packet loss.\n6. Escalate if infrastructure failure is suspected.',
            'risk_level': 'LOW',
            'automation_action': 'check_network'
        },
        {
            'title': 'DNS Resolution Troubleshooting',
            'category': 'NETWORK',
            'description': 'Procedure for investigating DNS resolution failures affecting internal or external services.',
            'symptoms': 'Domain cannot be resolved\nDNS timeout\nUnknown host error\nIntermittent name resolution',
            'steps': '1. Check DNS configuration.\n2. Test DNS resolution.\n3. Compare against a known DNS server.\n4. Verify local DNS cache.\n5. Check DNS service availability.\n6. Test the hostname again.',
            'risk_level': 'MEDIUM',
            'automation_action': 'check_dns'
        },
        {
            'title': 'Application Service Restart',
            'category': 'APPLICATION',
            'description': 'Procedure for recovering an application service that has stopped responding.',
            'symptoms': 'Application unavailable\nRequest timeout\nService inactive\nHTTP 500 errors',
            'steps': '1. Check application service status.\n2. Review application logs.\n3. Check system resource usage.\n4. Verify configuration.\n5. Restart the application service.\n6. Check service health.\n7. Test the application.',
            'risk_level': 'MEDIUM',
            'automation_action': 'restart_application'
        },
        {
            'title': 'Clear Application Cache',
            'category': 'APPLICATION',
            'description': 'Procedure for safely clearing temporary application cache when stale or corrupted cache data causes application problems.',
            'symptoms': 'Stale application data\nUnexpected cached response\nApplication behavior inconsistent with latest changes',
            'steps': '1. Confirm cache-related symptoms.\n2. Identify the application cache location.\n3. Verify that cache data can be safely regenerated.\n4. Clear the approved cache.\n5. Restart or reload the application if required.\n6. Verify normal application behavior.',
            'risk_level': 'LOW',
            'automation_action': 'clear_application_cache'
        },
        {
            'title': 'SSL Certificate Expiry Check',
            'category': 'SECURITY',
            'description': 'Procedure for investigating HTTPS certificate expiry or certificate-related warnings.',
            'symptoms': 'Browser certificate warning\nHTTPS connection error\nCertificate expired message\nTLS handshake failure',
            'steps': '1. Inspect the certificate expiry date.\n2. Verify the certificate domain.\n3. Check the certificate chain.\n4. Verify server certificate configuration.\n5. Renew or replace the certificate through the approved process.\n6. Verify HTTPS connectivity.',
            'risk_level': 'MEDIUM',
            'automation_action': 'check_ssl_certificate'
        },
        {
            'title': 'High CPU Usage Investigation',
            'category': 'SERVER',
            'description': 'Procedure for investigating unusually high CPU usage on an application or server.',
            'symptoms': 'CPU usage consistently high\nApplication slow\nSystem load elevated\nRequests timing out',
            'steps': '1. Check current CPU usage.\n2. Identify processes consuming CPU.\n3. Review recent application activity.\n4. Check application logs.\n5. Determine whether the process is expected.\n6. Restart only approved services if necessary.\n7. Monitor CPU usage after remediation.',
            'risk_level': 'MEDIUM',
            'automation_action': 'check_cpu_usage'
        },
        {
            'title': 'High Memory Usage Investigation',
            'category': 'SERVER',
            'description': 'Procedure for investigating high memory usage and possible memory pressure on a server.',
            'symptoms': 'Memory usage high\nApplication crashes\nOut of memory errors\nSystem becoming unresponsive',
            'steps': '1. Check memory utilization.\n2. Identify processes using memory.\n3. Review application logs.\n4. Check for abnormal memory growth.\n5. Restart approved services if required.\n6. Monitor memory after remediation.',
            'risk_level': 'MEDIUM',
            'automation_action': 'check_memory_usage'
        }
    ]
    
    for rb_info in runbooks_data:
        if not Runbook.objects.filter(title=rb_info['title']).exists():
            rb = Runbook.objects.create(
                title=rb_info['title'],
                category=rb_info['category'],
                description=rb_info['description'],
                symptoms=rb_info['symptoms'],
                steps=rb_info['steps'],
                risk_level=rb_info['risk_level'],
                automation_action=rb_info['automation_action'],
                created_by=admin
            )
            print(f"   [SUCCESS] Runbook created: {rb.runbook_number} - {rb.title}")
        else:
            print(f"   [INFO] Runbook '{rb_info['title']}' already exists.")

    print("=" * 60)
    print(" Seeding finished successfully!")
    print("=" * 60)

if __name__ == '__main__':
    run()
