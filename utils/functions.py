import hashlib
import os
import traceback
from datetime import datetime

import pytz
from asgiref.sync import async_to_sync
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import Message, SentCode, User, TermsOfService

load_dotenv()


def gen_hash(data: dict):
    txt = (f'{data.get("chatId") or ""}{data.get("merchantId") or ""}'
           f'{data.get("message") or ""}{data.get("timestamp") or ""}'
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

    # resp = requests.post("http://192.168.31.223:8107/api/notifications/v1/telegram/chat", json=data)
    # print(resp.status_code, resp.text)
    # try:
    #     jsn = resp.json()
    #     return jsn.get("status") == 1
    # except:
    #     traceback.print_exc()
    return False


@async_to_sync
async def a_send_code_request(account_name, phone):
    app = Client(account_name, os.getenv("API_ID"), os.getenv("API_HASH"), in_memory=True)
    await app.connect()
    sent_code: SentCode = await app.send_code(phone)
    code_hash = sent_code.phone_code_hash
    await app.disconnect()
    return code_hash


async def try_sign_in(account_name, phone, code, code_hash, password=None):
    app = Client(account_name, os.getenv("API_ID"), os.getenv("API_HASH"), in_memory=True)
    try:
        await app.connect()
        chat, terms, ok = await app.sign_in(phone_number=phone, phone_code_hash=code_hash, phone_code=code)
        chat: User
        terms: TermsOfService
        print(f"SIGNED_IN:", chat.first_name)
        print()
    except:
        traceback.print_exc()
    finally:
        await app.disconnect()


# send_code_request = async_to_sync(a_send_code_request, "send_code_request")

if __name__ == "__main__":
    a_send_code_request("name", "998904613136", int(os.getenv("API_ID")), os.getenv("API_HASH"))
