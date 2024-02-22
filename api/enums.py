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
            return "Merchant account not found"
        with Client(account.name, account.api_id, account.api_hash, session_string=account.session_string) as client:
            chat_id = get_chat_id(phone, client, contact_name)
            if chat_id:
                msg: Message = client.send_message(chat_id, message)
                return msg.id
            return "Unable to find user with phone number"
    except Exception:
        traceback.print_exc()
    finally:
        loop.close()
    return "Unknown error has been occurred"


if __name__ == "__main__":
    print(send_message("+998904613136qqqq", "test", "test"))
