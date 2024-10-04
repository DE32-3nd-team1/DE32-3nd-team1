from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


class message(BaseModel):
    message: str

app = FastAPI()

@app.post("/")
async def create_item(item: message):
    print(item)
    return item


