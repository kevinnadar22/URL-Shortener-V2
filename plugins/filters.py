from pyrogram.types import Message
from pyrogram.filters import create
from config import ADMINS, IS_PRIVATE, SOURCE_CODE

async def is_private_filter(_, __, m: Message):

    is_private = not bool(IS_PRIVATE)

    if m.from_user.id not in ADMINS and IS_PRIVATE:
        # await m.reply_text(f"This bot works only for ADMINS of this bot. Make your own Bot.\n\n[Source Code]({SOURCE_CODE})" , disable_web_page_preview=True)
        return False
    else:
        return True

    return is_private

is_private = create(is_private_filter)