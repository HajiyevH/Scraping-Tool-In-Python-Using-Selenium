from typing import Union , Optional,List,Dict,Any

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
async def get_recent_data(limit: int = 100, since_id: Optional[int] = None):
    return db.get_recent_laptops(limit=limit , since_id=since_id)