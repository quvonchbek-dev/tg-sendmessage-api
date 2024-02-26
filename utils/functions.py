import hashlib
import os
import traceback
from datetime import datetime

import pytz
import requests
from pyrogram.types import Message


def gen_hash(data: dict):
    txt = (f'{data.get("chatId", "")}{data.get("merchantId", "")}'
           f'{data.get("message", "")}{data.get("timestamp", "")}'
           f'{os.getenv("SECRET")}')
    return hashlib.sha256(txt.encode()).hexdigest()


def check_hash(data: dict):
    return data.get("hash") == gen_hash(data)


def send_message_to_server(msg: Message, merchant_id: str, phone=None):
    timestamp = int(datetime.now(pytz.timezone("Asia/Tashkent")).timestamp() * 1e6)
    data = dict(
        chatId=str(msg.chat.id),
        merchantId=merchant_id,
        phone=phone,
        username=msg.chat.username,
        photo=None,
        firstName=msg.chat.first_name,
        lastName=msg.chat.last_name,
        message=msg.text,
        timestamp=str(timestamp)
    )
    data["hash"] = gen_hash(data)
    print(data)

    # resp = requests.post("https://api-dev.lamenu.uz/api/notifications/v1/telegram/chat", json=data,
    #                      headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"})
    # print(resp.status_code, resp.text)
    # try:
    #     jsn = resp.json()
    #     return jsn.get("status") == 1
    # except:
    #     traceback.print_exc()
    return True
