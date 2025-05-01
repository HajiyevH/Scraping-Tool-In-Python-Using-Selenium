from typing import Union , Optional,List,Dict,Any
from icecream import ic
from fastapi import FastAPI, HTTPException
import asyncio
import src.database as db
app = FastAPI()

db.init_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/data/{limit}")
def read_item(limit : int):
    return db.get_recent_laptops(limit)

@app.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_data(limit: int = 100, since_date: Optional[str] = None):
    print(f"API Endpoint /recent received: limit={limit}, since_date='{since_date}' (Type: {type(since_date)})")

    return db.get_recent_laptops(limit=limit , since_date=since_date)

@app.get("/scrape",response_model=List[Dict[str, Any]])
async