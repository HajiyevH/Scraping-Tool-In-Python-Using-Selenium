from typing import Union

from fastapi import FastAPI
import src.database as db
app = FastAPI()

db.init_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/data/{limit}")
def read_item(limit : int):
    return db.get_recent_laptops(limit)