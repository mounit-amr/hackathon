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

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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

# Update status only
@app.patch("/items/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = status
    db.commit()
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

#this is after the ending
if __name__ == "__main__":
    port =  int(os.environ.get("PORT",8000))
    uvicorn.run("main:app",host="0.0.0.0", port=port)