import logging

from config import CHANNEL_ID, CHANNELS, FORWARD_MESSAGE, OWNER_ID
from database.users import get_user
from pyrogram import Client, filters
from utils import main_convertor_handler, update_stats, user_api_check

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# edit forwarded message
@Client.on_message(
    filters.chat(CHANNEL_ID)
    & (filters.channel | filters.group)
    & filters.incoming
    & ~filters.private
    & filters.forwarded
)
async def channel_forward_link_handler(c: Client, message):
    try:
        if FORWARD_MESSAGE and CHANNELS:
            
            user = await get_user(OWNER_ID)
            user_method = user["method"]
            vld = await user_api_check(user)
            if vld is not True and CHANNELS:
                return await c.send_message(OWNER_ID, "To use me in channel...\n\n" + vld)
            
            await main_convertor_handler(message, user=user)
            await message.delete()

            await update_stats(message, user_method)
    except Exception as e:
        logger.exception(e, exc_info=True)
