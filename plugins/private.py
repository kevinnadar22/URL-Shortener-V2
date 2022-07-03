from pyrogram import Client, filters
from utils import main_convertor_handler
from config import ADMINS, SOURCE_CODE
from database import db


# Private Chat

@Client.on_message((filters.inline_keyboard | filters.regex(r'https?://[^\s]+')) & filters.private)
async def private_link_handler(c, message):
    if message.from_user.id not in ADMINS:
        return await message.reply_text(f"This bot works only for ADMINS of this bot. Make your own Bot.\n\n"
                                 f"[Source Code]({SOURCE_CODE})")


    bot = await c.get_me()
    user_method = await db.get_bot_method(bot.username)
    await main_convertor_handler(c, message, user_method)



