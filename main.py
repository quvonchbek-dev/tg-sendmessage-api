import os
import random

import django
from dotenv import load_dotenv
from pyrogram import Client, filters, compose
from pyrogram.enums import ChatAction
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

load_dotenv()
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
from backend.models import Contact, TelegramAccount, Message as MessageModel


def send_message_to_server(phone, msg: Message, merchant_id, msg_type="TEXT"):
    data = dict(
        phone=f"+{phone}",
        merchantId=merchant_id,
        tgChatId=msg.chat.id,
        tgId=msg.chat.id,
        type=msg_type,
        text=msg.text,
        file=None
    )
    print(data)
    # resp = requests.post("https://api-dev.lamenu.uz/api/notifications/v1/telegram/chat", json=data,
    #                      headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"})
    # print(resp.status_code, resp.text)
    # try:
    #     jsn = resp.json()
    #     return jsn.get("status") == 1
    # except:
    #     traceback.print_exc()
    return random.choice([True, False])


def handle_messages(client: Client, msg: Message):
    current_user_id = client.me.id
    account: TelegramAccount = TelegramAccount.objects.filter(chat_id=current_user_id).first()
    contact = Contact.objects.filter(chat_id=msg.chat.id).first()
    # print(msg.chat.username, msg.from_user.username, msg.text)
    if account is None:
        print(f"Account not found - {current_user_id}")
        return
    if contact is None:
        print(f"Contact not found {msg.chat.id}")
        return
    client.send_chat_action(msg.chat.id, ChatAction.CHOOSE_STICKER)
    res = send_message_to_server(phone=None if contact is None else contact.phone, msg=msg,
                                 merchant_id=account.merchant_id)

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
        # app.start()
    compose(apps)
    print("stop")
    # idle()
    #
    # for app in apps:
    #     print("stop")
    #     app.stop()


if __name__ == "__main__":
    main()
