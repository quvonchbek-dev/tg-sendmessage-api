from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse

from utils import tg_api

app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.post("/sendMessage/")
async def send_message(phone: str, message: str, name: str = "Telegram User"):
    sent = await tg_api.send_message(phone, message, name)
    if sent:
        return JSONResponse({"msg": "Successfully sent"}, status_code=200)
    return JSONResponse({"msg": "Number not found"}, status_code=406)
