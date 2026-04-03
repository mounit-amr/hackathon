from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: str
    category: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    # status:Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    category: Optional[str]

    class Config:
        from_attributes = True
        
class PersonnelCreate(BaseModel):
    username: str  
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Schema ke liye token response after login
class Token(BaseModel):
    access_token: str  # the JWT token
    token_type: str    # always "bearer"
    
class ChatRequest(BaseModel):
    message: str
    
class AuditLogResponse(BaseModel):
    id: int
    user: str
    action: str
    resource: str
    resource_id: Optional[int]
    details: str
    ip_address: str
    timestamp: str

    class Config:
        from_attributes = True
        
class MaintenanceCreate(BaseModel):
    asset_id: int
    asset_name: str
    scheduled_date: str
    maintenance_type: str
    assigned_to: str
    priority: Optional[str] = "MEDIUM"
    notes: Optional[str] = None

class MaintenanceResponse(BaseModel):
    id: int
    asset_id: int
    asset_name: str
    scheduled_date: str
    maintenance_type: str
    assigned_to: str
    status: str
    priority: str
    notes: Optional[str]

    class Config:
        from_attributes = True