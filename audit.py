from sqlalchemy.orm import Session
import models
def log_action(
    db: Session,
    user: str,
    action: str,
    resource: str,
    details: str,
    resource_id: int = None,
    ip: str = "unknown"
):
    log = models.AuditLog(
        user=user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip
    )
    db.add(log)
    db.commit()