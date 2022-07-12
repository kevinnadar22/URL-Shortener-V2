
from pyrogram import Client, filters
from config import ADMINS, CHANNEL_ID, FORWARD_MESSAGE
from utils import main_convertor_handler
from database import db
from helpers import temp
# edit forwarded message


@Client.on_message(filters.chat(CHANNEL_ID) & (
        filters.channel | filters.group) & filters.incoming & ~filters.private & filters.forwarded)
async def channel_forward_link_handler(c:Client, message):
    if FORWARD_MESSAGE == "True" or FORWARD_MESSAGE is True:
        try:
            user_method = await db.get_bot_method(temp.BOT_USERNAME)
            if user_method is None:
                for chat_id in ADMINS:
                    await c.send_message(chat_id=chat_id, text="Set your /method to convert channel posts")
                return
            else:
                await main_convertor_handler(message, user_method)
            await message.delete()
        except Exception as e:
            print(e)
