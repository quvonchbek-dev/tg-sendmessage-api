import asyncio
import os
import traceback

from pyrogram import Client
from pyrogram.errors import exceptions
from pyrogram.raw.types.contacts import ImportedContacts
from pyrogram.types import InputPhoneContact

from utils import config


async def register_account():
    client = Client("account", config.API_ID, config.API_HASH)
    await client.start()
    s_str = await client.export_session_string()
    await client.stop()
    return s_str


async def send_message(phone, message, name):
    try:
        async with Client("account", session_string=os.getenv("SESSION_STRING")) as client:
            contact: ImportedContacts = await client.import_contacts([InputPhoneContact(phone, name)])
            user_id = contact.users[0].id
            await client.send_message(user_id, message)
    except (KeyError, exceptions.PeerIdInvalid, IndexError):
        print(f"Phone number not found: {phone}")
    except Exception as ex:
        traceback.print_exc()
    else:
        return True
    return False


if __name__ == "__main__":
    s = asyncio.run(register_account())
    print(s)
