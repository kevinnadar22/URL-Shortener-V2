import logging

from config import CHANNEL_ID, CHANNELS, OWNER_ID
from database.users import get_user
from pyrogram import Client, filters
from utils import main_convertor_handler, update_stats, user_api_check

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Channel


@Client.on_message(
    ~filters.forwarded
    & filters.chat(CHANNEL_ID)
    & (filters.channel | filters.group)
    & filters.incoming
    & ~filters.private
    & ~filters.forwarded
)
async def channel_link_handler(c: Client, message):
    if CHANNELS:
        user = await get_user(OWNER_ID)
        user_method = user["method"]
        vld = await user_api_check(user)
        if vld is not True and CHANNELS:
            return await c.send_message(OWNER_ID, f"To use me in channel...{vld}")

        try:
            await main_convertor_handler(message, True, user=user)
            await update_stats(message, user_method)
        except Exception as e:
            logger.exception(e, exc_info=True)


@Client.on_message(filters.command("test") & filters.user(OWNER_ID))
async def test(c: Client, message):
    m_id = 3012
    c_id = 0
    message = await c.get_messages(c_id, m_id)
    user = await get_user(OWNER_ID)
    await main_convertor_handler(message, True, user)
