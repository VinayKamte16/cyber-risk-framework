"""
Database module for cybersecurity risk scoring framework.
Handles database operations and models.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Create SQLAlchemy base class
Base = declarative_base()

# Create engine and session factory
engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./security.db"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.session = SessionLocal()
    
    def close(self):
        """Close the database session."""
        self.session.close()
    
    def add_security_event(self, event_data: Dict[str, Any]) -> None:
        """Add a security event to the database."""
        event = SecurityEvent(**event_data)
        self.session.add(event)
        self.session.commit()
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events."""
        events = self.session.query(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(limit).all()
        return [event.__dict__ for event in events]
    
    def add_vulnerability(self, vuln_data: Dict[str, Any]) -> None:
        """Add a vulnerability to the database."""
        vuln = Vulnerability(**vuln_data)
        self.session.add(vuln)
        self.session.commit()
    
    def get_active_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Get active vulnerabilities."""
        vulns = self.session.query(Vulnerability).filter(Vulnerability.status == "active").all()
        return [vuln.__dict__ for vuln in vulns]
    
    def add_threat_intel(self, intel_data: Dict[str, Any]) -> None:
        """Add threat intelligence data to the database."""
        intel = ThreatIntelligence(**intel_data)
        self.session.add(intel)
        self.session.commit()
    
    def get_recent_threats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent threat intelligence data."""
        threats = self.session.query(ThreatIntelligence).order_by(ThreatIntelligence.timestamp.desc()).limit(limit).all()
        return [threat.__dict__ for threat in threats]
    
    def add_asset(self, asset_data: Dict[str, Any]) -> None:
        """Add an asset to the database."""
        asset = Asset(**asset_data)
        self.session.add(asset)
        self.session.commit()
    
    def get_all_assets(self) -> List[Dict[str, Any]]:
        """Get all assets."""
        assets = self.session.query(Asset).all()
        return [asset.__dict__ for asset in assets]

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SecurityEvent(Base):
    """Model for security events."""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)
    severity = Column(String)
    source = Column(String)
    description = Column(String)
    details = Column(JSON)
    status = Column(String, default="new")

class Vulnerability(Base):
    """Model for vulnerabilities."""
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String, unique=True)
    name = Column(String)
    description = Column(String)
    severity = Column(String)
    affected_assets = Column(JSON)
    remediation = Column(String)
    status = Column(String, default="active")
    discovered_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class ThreatIntelligence(Base):
    """Model for threat intelligence data."""
    __tablename__ = "threat_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    threat_type = Column(String)
    indicators = Column(JSON)
    description = Column(String)
    confidence_score = Column(Float)
    mitigation = Column(String)

class Asset(Base):
    """Model for assets."""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    asset_type = Column(String)
    ip_address = Column(String)
    hostname = Column(String)
    os = Column(String)
    criticality = Column(String)
    last_scan = Column(DateTime)
    vulnerabilities = Column(JSON)
    status = Column(String, default="active") 