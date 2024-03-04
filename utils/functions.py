import asyncio
import hashlib
import os
import traceback
from datetime import datetime

import pytz
import requests
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.errors import PhoneCodeExpired
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

    resp = requests.post(f"{os.getenv('SERVER_ENDPOINT')}/api/notifications/v1/telegram/chat", json=data)
    print(resp.status_code, resp.text)
    try:
        jsn = resp.json()
        return jsn.get("status") == 1
    except:
        traceback.print_exc()
    return False


# @async_to_sync
async def send_code_request(account_name, phone, test_mode=False):
    app = Client(account_name, os.getenv("API_ID"), os.getenv("API_HASH"), test_mode=test_mode)
    await app.connect()
    sent_code: SentCode = await app.send_code(phone)
    code_hash = sent_code.phone_code_hash
    await app.disconnect()
    return code_hash


async def try_sign_in2(account_name, phone, code, code_hash, password=None, test_mode=False):
    app = Client(account_name, os.getenv("API_ID"), os.getenv("API_HASH"))
    try:
        chat, terms, ok = await app.sign_in(phone_number=phone, phone_code_hash=code_hash, phone_code=code)
        chat: User
        terms: TermsOfService
        print(f"SIGNED_IN:", chat.first_name)
        return app.load_session()
    except PhoneCodeExpired:
        print("Phone code expired. Requesting a new one...")
        code_hash = await send_code_request(account_name, phone)
        code = input("Enter the new code: ")
        return await try_sign_in(account_name, phone, code, code_hash, password=password, test_mode=test_mode)
    except:
        traceback.print_exc()
    finally:
        await app.disconnect()


# @async_to_sync
async def try_sign_in(account_name, phone, code, code_hash, password=None, test_mode=False):
    app = Client(account_name, os.getenv("API_ID"), os.getenv("API_HASH"), test_mode=test_mode)
    try:
        await app.connect()
        chat, terms, ok = await app.sign_in(phone_number=phone, phone_code_hash=code_hash, phone_code=code)
        chat: User
        terms: TermsOfService
        print(f"SIGNED_IN:", chat.first_name)
        return app.load_session()
    except:
        traceback.print_exc()
    finally:
        await app.disconnect()


async def main():
    name = "abcd"
    phone = "+998904613136"
    code_hash = await send_code_request(name, phone, test_mode=True)
    print(code_hash)
    # code_hash = "926aa568cb51265734"
    code = input("CODE:")
    session_string = await try_sign_in2(account_name=name, phone=phone, code=code, code_hash=code_hash, test_mode=True)
    print(session_string)


if __name__ == "__main__":
    asyncio.run(main())
