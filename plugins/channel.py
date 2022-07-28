from config import CHANNEL_ID, CHANNELS, ADMINS
from pyrogram import Client, filters
from utils import main_convertor_handler, update_stats
from database import db
from helpers import temp
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


# Channel

@Client.on_message(~filters.forwarded & filters.chat(CHANNEL_ID) & (
                filters.channel | filters.group) & filters.incoming & ~filters.private &
        ~filters.forwarded)
async def channel_link_handler(c:Client, message):
    user_method = await db.get_bot_method(temp.BOT_USERNAME)

    if CHANNELS:
        try:
            if user_method is None:
                for chat_id in ADMINS:
                    await c.send_message(chat_id=chat_id, text="Set your /method to convert channel posts")
                return
            else:
                await main_convertor_handler(message, user_method, True)
                # Updating DB stats
                await update_stats(message, user_method)

        except Exception as e:
            logger.error(e)