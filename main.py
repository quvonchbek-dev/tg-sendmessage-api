import os

import django
from dotenv import load_dotenv
from pyrogram import Client, filters, compose
from pyrogram.enums import ChatAction
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from utils.functions import send_message_to_server

load_dotenv()
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
from backend.models import Contact, TelegramAccount, Message as MessageModel


def handle_messages(client: Client, msg: Message):
    current_user_id = client.me.id
    account: TelegramAccount = TelegramAccount.objects.filter(chat_id=current_user_id).first()
    contact = Contact.objects.filter(chat_id=msg.chat.id).first()
    if account is None:
        print(f"Account not found - {current_user_id}")
        return
    client.send_chat_action(msg.chat.id, ChatAction.CHOOSE_STICKER)
    res = send_message_to_server(
        phone=None if contact is None else contact.phone,
        msg=msg, merchant_id=account.merchant_id
    )

    if not res:
        MessageModel.objects.create(
            contact=contact, merchant=account, body=msg.text,
            status=MessageModel.Status.SERVER_NOT_RECEIVED,
            msg_id=msg.id
        )
    else:
        client.read_chat_history(msg.chat.id, msg.id)


def filter_my_messages(_, client: Client, msg: Message):
    return client.me.id != msg.from_user.id


def main():
    accounts = TelegramAccount.objects.all()
    apps = [Client(account.name, account.api_id, account.api_hash, session_string=account.session_string) for account in
            accounts]
    for app in apps:
        app.add_handler(MessageHandler(handle_messages, filters=filters.private & filters.create(filter_my_messages)))

    compose(apps)
    print("Sessions are stopped.")


if __name__ == "__main__":
    main()
