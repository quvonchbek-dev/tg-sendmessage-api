import asyncio
import os
import traceback

import django
from pyrogram import Client
from pyrogram.enums import ChatAction
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.types.contacts import ImportedContacts
from pyrogram.types import Message, Chat, InputPhoneContact

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from backend.models import TelegramAccount, Contact


class CustomStatus:
    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return f"{self.description}"

    def __int__(self):
        return self.code

    def dict(self):
        return dict(code=self.code, detail=self.description)


class CustomStatusCodes:
    SUCCESS = CustomStatus(1, "Success.")
    UNKNOWN_ERROR_OCCURRED = CustomStatus(-1, "Unknown error has been occurred.")
    MERCHANT_NOT_FOUND = CustomStatus(-2, "Merchant account not found.")
    UNABLE_TO_FIND_USER = CustomStatus(-3, "Unable to find user with given data.")
    VALIDATION_ERROR = CustomStatus(-4, "Request body is not valid.")
    INVALID_CREDENTIALS = CustomStatus(-5, "Invalid credentials provided.")


def get_chat_id(phone: str, client: Client, contact_name="Telegram Client"):
    if not phone:
        return None
    contact: Contact = Contact.objects.filter(phone=phone).first()
    if contact is None:
        imported_contacts: ImportedContacts = client.import_contacts([InputPhoneContact(phone, contact_name)])
        users = imported_contacts.users
        if len(users):
            chat_id = users[0].id
            Contact.objects.create(phone=phone, name=contact_name, chat_id=chat_id)
            return chat_id
        return
    try:
        chat: Chat = client.get_chat(contact.chat_id)
        return chat.id
    except PeerIdInvalid:
        imported_contacts: ImportedContacts = client.import_contacts([InputPhoneContact(phone, contact_name)])
        users = imported_contacts.users
        if len(users):
            chat_id = users[0].id
            contact.name = contact_name
            contact.chat_id = chat_id
            contact.save()
            return chat_id
    except Exception as ex:
        traceback.print_exc()


def send_message(data: dict):
    del data["hash"], data["timestamp"]
    chat_id = data.get("chatId")
    username = data.get("username")
    phone = data.get("phone")
    name = (data.get("firstName") or "Firstname") + " " + (data.get("lastName") or "Surname")
    print(name)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        account: TelegramAccount = TelegramAccount.objects.filter(merchant_id=data.get("merchantId")).first()
        if account is None:
            return CustomStatusCodes.MERCHANT_NOT_FOUND
        with Client(account.name, account.api_id, account.api_hash, session_string=account.session_string) as client:
            client: Client
            identifier = None
            if chat_id:
                try:
                    chat: Chat = client.get_chat(int(chat_id))
                    identifier = chat.id
                except:
                    pass
                    # traceback.print_exc()
            if not identifier and username:
                try:
                    client.get_chat(username)
                    identifier = username
                except:
                    pass
            if not identifier and phone:
                identifier = get_chat_id(phone, client, name)
            if not identifier:
                return CustomStatusCodes.UNABLE_TO_FIND_USER
            client.send_chat_action(identifier, ChatAction.TYPING)
            msg: Message = client.send_message(identifier, data.get("message"))
            location = data.get("location")
            if location:
                client.send_location(chat_id=identifier, latitude=location.get("latitude"), longitude=location.get("longitude"))
            chat = client.get_chat(identifier)
            data["username"] = chat.username
            data["chatId"] = chat.id
            data["firstName"] = chat.first_name
            data["lastName"] = chat.last_name
            data["msgId"] = msg.id
            data["status"] = CustomStatusCodes.SUCCESS.dict()
            return data
    except Exception:
        traceback.print_exc()
    finally:
        loop.close()
    return CustomStatusCodes.UNKNOWN_ERROR_OCCURRED


if __name__ == "__main__":
    print()
