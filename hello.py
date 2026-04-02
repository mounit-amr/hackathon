from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    Name : str
    model : int
    type : str



database = {1:{"name" : "hayabhusa",
               "model" : 2026,
               "type" : "drag"},
            2:{"name" : "ducati",
               "model": 2024,
               "type" : "street"}}

@app.get("/")
def home():
    return {"status online"}

@app.get("/helo")
def trial():
    return "without curly brackets"

@app.get("/fetch_item/{id}")
def prod(id : int):
    return database[id]

@app.post("/addition/{id}")
def adding(id : int , item : Item):
    if id in database:
        return {"error" : "bike already exists"}
    
    database[id] = item.dict()
    return database[id]

