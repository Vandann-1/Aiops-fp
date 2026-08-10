import os
import django

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiops_service_desk.settings')
django.setup()

from incidents.models import Incident, IncidentActivity
from runbooks.models import Runbook

def run():
    print("=" * 60)
    print(" Clearing Development Incident & Runbook Data...")
    print("=" * 60)
    
    activity_count = IncidentActivity.objects.all().delete()[0]
    incident_count = Incident.objects.all().delete()[0]
    runbook_count = Runbook.objects.all().delete()[0]
    
    print(f"   [SUCCESS] Deleted {activity_count} Incident Activity logs.")
    print(f"   [SUCCESS] Deleted {incident_count} Incident tickets.")
    print(f"   [SUCCESS] Deleted {runbook_count} Runbook knowledge base records.")
    print("=" * 60)
    print(" Database cleared successfully!")
    print("=" * 60)

if __name__ == '__main__':
    run()
