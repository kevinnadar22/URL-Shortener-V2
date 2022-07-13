from pyrogram import Client, filters
from utils import main_convertor_handler
from config import ADMINS, SOURCE_CODE
from database import db
from helpers import temp
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.ERROR)

# Private Chat

@Client.on_message(filters.private & filters.incoming)
async def private_link_handler(c, message):
    if message.from_user.id not in ADMINS:
        return await message.reply_text(f"This bot works only for ADMINS of this bot. Make your own Bot.\n\n[Source Code]({SOURCE_CODE})")

    user_method = await db.get_bot_method(temp.BOT_USERNAME)
    try:
        await main_convertor_handler(message, user_method)
    except Exception as e:
        logger.exception(e)

