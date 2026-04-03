# audit.py
from sqlalchemy.orm import Session
import models

def log_action(db: Session, user: str, action: str, resource: str, details: str, 
               affected_count: int = 1, resource_id: int = None, ip: str = "unknown"):
    
    is_anomaly = 0
    # Threshold logic: if more than 100 entries are deleted at once
    if action == "DELETE" and affected_count > 100:
        is_anomaly = 1
        # Block the user in the database
        db.query(models.Personnel).filter(models.Personnel.username == user).update({"is_blocked": 1})
    
    log = models.AuditLog(
        user=user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip,
        affected_count=affected_count,
        is_anomaly=is_anomaly
    )
    db.add(log)
    db.commit()
    return is_anomaly