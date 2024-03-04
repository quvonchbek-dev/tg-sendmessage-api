import os
import traceback

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
from pyrogram.types import SentCode


class TgSession:
    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone_number = phone
        self.phone_code_hash: str = None
        self.app: Client = None

    async def init(self):
        self.app = Client(self.name, os.getenv("API_ID"), os.getenv("API_HASH"), test_mode=True)
        await self.app.connect()

    async def send_code(self, code_hash=None) -> str:
        if not self.app.is_connected:
            await self.app.connect()
        self.sent_code: SentCode
        if code_hash:
            sent_code = await self.app.resend_code(self.phone_number, phone_code_hash=code_hash)
            self.phone_code_hash = sent_code.phone_code_hash
        elif self.phone_code_hash:
            sent_code = await self.app.resend_code(self.phone_number, phone_code_hash=self.phone_code_hash)
            self.phone_code_hash = sent_code.phone_code_hash
        else:
            self.phone_code_hash = (await self.app.send_code(self.phone_number)).phone_code_hash
        return self.phone_code_hash

    async def sign_in(self, phone_code, code_hash=None):
        try:
            if code_hash:
                self.phone_code_hash = code_hash
            await self.app.sign_in(self.phone_number, self.phone_code_hash, phone_code)
            return 1
        except SessionPasswordNeeded:
            return -1
        except PhoneCodeInvalid:
            return -2
        except Exception:
            traceback.print_exc()
            return 0

    async def check_password(self, password):
        try:
            await self.app.check_password(password)
            return True
        except Exception:
            traceback.print_exc()
            return False

    async def get_session_string(self):
        s_str = await self.app.export_session_string()
        return s_str

    def __del__(self):
        print("Deleted", self.name)

    def __str__(self):
        return str(self.name)
