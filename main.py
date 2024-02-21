from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from utils import tg_api

app = FastAPI()


class Message(BaseModel):
    phone: str
    message: str
    name: str | None = ""


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.post("/sendMessage/")
async def send_message(msg: Message):
    sent = await tg_api.send_message(msg.phone, msg.message, msg.name or "Telegram User")
    if sent:
        return JSONResponse({"msg": "Successfully sent"}, status_code=200)
    return JSONResponse({"msg": "Number not found"}, status_code=406)
