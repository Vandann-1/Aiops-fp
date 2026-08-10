import os
import django

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiops_service_desk.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile
from runbooks.models import Runbook

User = get_user_model()

def run():
    print("=" * 60)
    print(" Seeding Main Runbook Procedures Only...")
    print("=" * 60)
    
    # Get or create IT Admin user
    admin_username = 'admin'
    admin_password = 'admin1234'
    admin = User.objects.get(username=admin_username)
        
    # Clear existing runbooks first
    Runbook.objects.all().delete()
    print("   [INFO] Cleaned old runbooks.")

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
        print(f"   [SUCCESS] Seeded: {rb.runbook_number} - {rb.title}")
    
    print("=" * 60)
    print(" Runbooks seeded successfully!")
    print("=" * 60)

if __name__ == '__main__':
    run()
