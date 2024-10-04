from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/")
async def receive_message(message: Message):
    # 받은 메시지를 로그에 출력합니다.
    print(message.message)
    return {"Received message": message.message}

