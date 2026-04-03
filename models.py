from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    status = Column(String, default="active")
    category = Column(String, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
class Personnel(Base):
    __tablename__ = "personnel"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")
    is_blocked = Column(Integer, default=0)
    
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    action = Column(String)
    resource = Column(String)
    resource_id = Column(Integer, nullable=True)
    details = Column(String)
    ip_address = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
    affected_count = Column(Integer, default=1) # Track how many entries were impacted
    is_anomaly = Column(Integer, default=0) #security flagged
    
class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer)
    asset_name = Column(String)
    scheduled_date = Column(String)
    maintenance_type = Column(String)  # ROUTINE, EMERGENCY, INSPECTION
    assigned_to = Column(String)
    status = Column(String, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    priority = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())