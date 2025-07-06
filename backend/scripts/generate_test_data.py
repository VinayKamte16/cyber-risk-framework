"""
Generate test data for the cybersecurity risk framework dashboard.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SecurityEvent, Vulnerability, ThreatIntelligence, Asset, Base, engine, SessionLocal
from datetime import datetime, timedelta
import random
import json

def generate_test_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Generate Assets
        assets = [
            Asset(
                name=f"Server-{i}",
                type="server" if i % 3 == 0 else "cloud" if i % 3 == 1 else "workstation",
                ip_address=f"192.168.1.{i+10}",
                criticality=random.randint(1, 5),
                owner=f"Department {i%5 + 1}",
                asset_metadata={"location": "Data Center A", "os": "Linux"}
            ) for i in range(10)
        ]
        db.add_all(assets)

        # Generate Security Events
        events = []
        for i in range(50):
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
            events.append(SecurityEvent(
                timestamp=timestamp,
                event_type=random.choice(['malware', 'network', 'authentication', 'system']),
                source_ip=f"192.168.1.{random.randint(1, 255)}",
                destination_ip=f"10.0.0.{random.randint(1, 255)}",
                severity=random.randint(1, 5),
                description=f"Security event {i+1}",
                raw_data=json.dumps({"alert_id": f"ALERT-{i}", "details": "Sample alert data"})
            ))
        db.add_all(events)

        # Generate Vulnerabilities
        vulns = []
        for i in range(20):
            vulns.append(Vulnerability(
                cve_id=f"CVE-2023-{1000+i}",
                cvss_score=random.uniform(1.0, 10.0),
                description=f"Sample vulnerability {i+1}",
                affected_systems=json.dumps([f"Server-{j}" for j in range(random.randint(1, 3))]),
                remediation=f"Apply patch {i+1}",
                discovery_date=datetime.now() - timedelta(days=random.randint(1, 30))
            ))
        db.add_all(vulns)

        # Generate Threat Intelligence
        threats = []
        for i in range(30):
            threats.append(ThreatIntelligence(
                indicator=f"indicator-{i}",
                type=random.choice(['ip', 'domain', 'hash']),
                confidence_score=random.uniform(0.1, 1.0),
                last_seen=datetime.now() - timedelta(hours=random.randint(1, 48)),
                source="VirusTotal",
                context=json.dumps({"malware_family": f"malware-{i}", "tags": ["suspicious"]})
            ))
        db.add_all(threats)

        db.commit()
        print("Test data generated successfully!")

    except Exception as e:
        print(f"Error generating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_data() 