from sqlalchemy.orm import Session
import models
from main import manager 

async def log_action(db: Session, user: str, action: str, resource: str, details: str, 
               affected_count: int = 1, resource_id: int = None, ip: str = "unknown"):
    
    is_anomaly = 0
    if action == "DELETE" and affected_count > 10: 
        is_anomaly = 1
        db.query(models.Personnel).filter(models.Personnel.username == user).update({"is_blocked": 1})
        
        await manager.broadcast({
            "type": "FORCE_LOGOUT",
            "user": user,
            "reason": f"CRITICAL: Mass {action} detected ({affected_count} items)."
        })
    
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