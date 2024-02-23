import asyncio
import os
import traceback

import django
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.types.contacts import ImportedContacts
from pyrogram.types import InputPhoneContact
from pyrogram.types import Message, Chat

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

    def __dict__(self):
        return dict(code=self.code, message=self.description)


class CustomStatusCodes:
    SUCCESS = CustomStatus(0, "Success.")
    UNKNOWN_ERROR_OCCURRED = CustomStatus(-1, "Unknown error has been occurred.")
    MERCHANT_NOT_FOUND = CustomStatus(-2, "Merchant account not found.")
    UNABLE_TO_FIND_USER = CustomStatus(-3, "Unable to find user with phone number.")
    VALIDATION_ERROR = CustomStatus(-4, "Request body is not valid.")


def get_chat_id(phone: str, client: Client, contact_name="Telegram Client"):
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


def send_message(phone, message, merchant_id, contact_name="Telegram Client"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    phone = "".join(filter(lambda x: x.isdigit(), phone))
    try:
        account: TelegramAccount = TelegramAccount.objects.filter(merchant_id=merchant_id).first()
        if account is None:
            return CustomStatusCodes.MERCHANT_NOT_FOUND, None
        with Client(account.name, account.api_id, account.api_hash, session_string=account.session_string) as client:
            chat_id = get_chat_id(phone, client, contact_name)
            if chat_id:
                msg: Message = client.send_message(chat_id, message)
                return CustomStatusCodes.SUCCESS, msg.id
            return CustomStatusCodes.UNABLE_TO_FIND_USER, None
    except Exception:
        traceback.print_exc()
    finally:
        loop.close()
    return CustomStatusCodes.UNKNOWN_ERROR_OCCURRED, None


if __name__ == "__main__":
    print(send_message("+998904613136", "test", "test"))
