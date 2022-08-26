import functools
from pyrogram.types import Message
from config import ADMINS, IS_PRIVATE
from pyrogram import Client

def private_use(func):
    @functools.wraps(func)
    async def wrapper(client: "Client", message: "Message"):
        chat_id = getattr(message.from_user, "id", None)
        if IS_PRIVATE and chat_id not in ADMINS:
            await message.reply_text("This bot only works for Admins. Make your own [Bot](https://github.com/kevinnadar22/URL-Shortener-V2)", quote=True, disable_web_page_preview=True)
            return
        return await func(client, message)
    return wrapper