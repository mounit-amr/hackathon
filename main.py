from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from schemas import ItemCreate, ItemUpdate, ItemResponse
from auth import hash_password, verify_password, create_access_token
from schemas import ItemCreate, ItemUpdate, ItemResponse, PersonnelCreate, LoginRequest,ChatRequest
from gemini import generate_response
from fastapi.middleware.cors import CORSMiddleware
from auth import hash_password, verify_password, create_access_token, get_current_user
import os, uvicorn
from contextlib import asynccontextmanager
from audit import log_action
from fastapi import Request
from fastapi import WebSocket, WebSocketDisconnect


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)


# app = FastAPI()
@app.get("/") 
def root():
    return {"message": "API is running"}

@app.get("/chat")
def chat(prompt: str):
    try:
        return {"response": generate_response(prompt)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/test")
def test():
    return {"status" : "working"}

@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    new_item = models.Item(
        name=item.name,
        description=item.description,
        category=item.category
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/items", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

@app.get("/items/{id}", response_model=ItemResponse)
def get_item(id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{id}", response_model=ItemResponse)
def update_item(id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    existing = db.query(models.Item).filter(models.Item.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.name is not None:
        existing.name = item.name
    if item.description is not None:
        existing.description = item.description
    if item.status is not None:
        existing.status = item.status
    if item.category is not None:
        existing.category = item.category
    db.commit()
    db.refresh(existing)
    return existing

@app.delete("/items/{id}")
def delete_item(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": f"Item {id} deleted"}

# Register route — creates new user
@app.post("/auth/register")
def register(personnel: PersonnelCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing = db.query(models.Personnel).filter(
        models.Personnel.username == personnel.username
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password before saving
    hashed = hash_password(personnel.password)

    # Create new personnel object
    new_user = models.Personnel(
        username=personnel.username,
        password=hashed,  # save hashed not plain
        role=personnel.role
    )

    # Save to database
    db.add(new_user)
    db.commit()
    return {"message": "Personnel registered successfully"}


# Login route — returns JWT token
@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(models.Personnel).filter(
        models.Personnel.username == request.username
    ).first()

    # If user not found OR password wrong — reject
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token with username and role inside
    token = create_access_token({
        "sub": user.username,  # sub = subject = who this token belongs to
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}

@app.post("/ai/chat")
def chat(request: ChatRequest):
    result = generate_response(request.message)
    return {"response": result}
from gemini import generate_response

@app.post("/ai/chat")
def chat(request: ChatRequest):
    result = generate_response(request.message)
    return {"response": result}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Search items by name
@app.get("/items/search")
def search_items(query: str, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(
        models.Item.name.contains(query)
    ).all()

# Filter items by status
@app.get("/items/status/{status}")
def get_by_status(status: str, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(
        models.Item.status == status
    ).all()

# Stats endpoint
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Item).count()
    active = db.query(models.Item).filter(models.Item.status == "active").count()
    return {
        "total_items": total,
        "active_items": active,
        "inactive_items": total - active
    }

@app.patch("/items/{id}/status")
async def update_status(id: int, status: str, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.status = status
    db.commit()
 
    await manager.broadcast({
        "item_id": id,
        "new_status": status,
        "type": "STATUS_UPDATE"
    })
    
    return {"message": f"Status updated to {status}"}

# Health check
@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except:
        db_status = "disconnected"
    return {
        "status": "online",
        "database": db_status
    }
    
# POST - protected
@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    new_item = models.Item(
        name=item.name,
        description=item.description,
        category=item.category
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# DELETE - protected
@app.delete("/items/{id}")
def delete_item(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": f"Item {id} deleted"}



# Get all audit logs
@app.get("/audit/logs")
def get_audit_logs(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return db.query(models.AuditLog).order_by(
        models.AuditLog.timestamp.desc()
    ).all()

# Get logs for specific resource
@app.get("/audit/logs/{resource}")
def get_resource_logs(resource: str, db: Session = Depends(get_db)):
    return db.query(models.AuditLog).filter(
        models.AuditLog.resource == resource
    ).all()

@app.post("/missions")
def create_mission(
    mission: ItemCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_mission = models.Item(
        name=mission.name,
        description=mission.description
    )
    db.add(new_mission)
    db.commit()
    db.refresh(new_mission)

    # Log the action
    log_action(
        db=db,
        user=current_user,
        action="CREATE",
        resource="mission",
        resource_id=new_mission.id,
        details=f"Mission {mission.name} created",
        ip=request.client.host
    )

    return new_mission

@app.delete("/items/bulk")
def bulk_delete(ids: list[int], request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    count = len(ids)
    
    # Perform deletion...
    
    # Log and check for anomaly
    was_blocked = log_action(
        db=db,
        user=current_user,
        action="DELETE",
        resource="items",
        details=f"Attempted bulk delete of {count} items",
        affected_count=count,
        ip=request.client.host
    )
    
    if was_blocked:
        return {"message": "Action flagged. User has been blocked for security."}
    
    return {"message": f"Successfully deleted {count} items"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/tracking")
async def websocket_tracking(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
#this is after the ending
