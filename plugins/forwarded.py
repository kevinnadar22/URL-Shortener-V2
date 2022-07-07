
from pyrogram import Client, filters
from config import CHANNEL_ID, FORWARD_MESSAGE
from utils import main_convertor_handler
from database import db
# edit forwarded message


@Client.on_message(filters.chat(CHANNEL_ID) & (
        filters.channel | filters.group) & filters.incoming & ~filters.private & filters.forwarded)
async def channel_forward_link_handler(c:Client, message):
    if FORWARD_MESSAGE == "True" or FORWARD_MESSAGE is True:
        try:
            username = await c.get_me()
            user_method = await db.get_bot_method(username.username)
            await main_convertor_handler(c, message, user_method)
            await message.delete()
        except Exception as e:
            print(e)
