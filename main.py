import asyncio
import logging
import os
import signal
from signal import signal as signal_fn, SIGINT, SIGTERM, SIGABRT
from typing import Dict

import django
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from utils.functions import send_message_to_server

load_dotenv()
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    # os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()
from backend.models import Contact, TelegramAccount, Message as MessageModel

log = logging.getLogger(__name__)

# Signal number to name
signals = {
    k: v for v, k in signal.__dict__.items()
    if v.startswith("SIG") and not v.startswith("SIG_")
}


async def handle_messages(client: Client, msg: Message):
    current_user_id = client.me.id
    account: TelegramAccount = await TelegramAccount.objects.filter(chat_id=current_user_id).afirst()
    contact = await Contact.objects.filter(chat_id=msg.chat.id).afirst()
    if account is None:
        logging.error(f"Account not found - {current_user_id}")
        return
    await client.send_chat_action(msg.chat.id, ChatAction.TYPING)
    res = send_message_to_server(
        phone=None if contact is None else contact.phone,
        msg=msg, merchant_id=account.merchant_id
    )

    if not res:
        await MessageModel.objects.acreate(
            contact=contact, merchant=account, body=msg.text,
            status=MessageModel.Status.SERVER_NOT_RECEIVED,
            msg_id=msg.id
        )
    else:
        await client.read_chat_history(msg.chat.id, msg.id)


async def filter_my_messages(_, client: Client, msg: Message):
    return client.me.id != msg.from_user.id


async def update_changes(data: Dict[str | int, Client]):
    current_working = set(data.keys())
    current_in_db = set()
    async for acc in TelegramAccount.objects.all().values("chat_id"):
        current_in_db.add(acc.get("chat_id"))
    deleted = current_working - current_in_db
    news = current_in_db - current_working

    for d in deleted:
        app = data.get(d)
        chat = await app.get_me()
        logging.info(f"DELETED - {chat.phone_number} - {chat.id} - {chat.first_name}")
        await app.stop()
        del data[d]
    for n in news:
        account = await TelegramAccount.objects.aget(chat_id=n)
        app = Client(account.name, account.api_id, account.api_hash, session_string=account.session_string)
        app.add_handler(MessageHandler(handle_messages, filters=filters.private & filters.create(filter_my_messages)))
        await app.start()
        chat = await app.get_me()
        logging.info(f"NEW ACCOUNT - {chat.phone_number} - {chat.id} - {chat.first_name}")
        data[account.chat_id] = app


async def main():
    accounts = TelegramAccount.objects.all()
    apps = {}
    async for account in accounts:
        app = Client(account.name, account.api_id, account.api_hash, session_string=account.session_string)
        await app.start()
        app.add_handler(MessageHandler(handle_messages, filters=filters.private & filters.create(filter_my_messages)))
        apps[account.chat_id] = app

    # IDLE START
    task = None
    update_task = None

    def signal_handler(signum, __):
        logging.info(f"Stop signal received ({signals[signum]}). Exiting...")
        task.cancel()
        update_task.cancel()

    for s in (SIGINT, SIGTERM, SIGABRT):
        signal_fn(s, signal_handler)

    while True:
        logging.info("Updating accounts")
        task = asyncio.create_task(asyncio.sleep(10))
        update_task = asyncio.create_task(update_changes(apps))
        try:
            await update_task
            logging.info(apps)
            await task
        except asyncio.CancelledError:
            break
    # IDLE END
    for chat_id, app in apps.items():
        await app.stop()
        del apps[chat_id]
    logging.info("Sessions are stopped.")


if __name__ == "__main__":
    asyncio.run(main())
