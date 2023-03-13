import logging
from config import LOG_CHANNEL
from database.users import get_user
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import extract_link, main_convertor_handler, update_stats, user_api_check
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from plugins.filters import private_use

logger = logging.getLogger(__name__)

# Private Chat
@Client.on_message(filters.private & filters.incoming)
@private_use
async def private_link_handler(c: Client, message: Message):
    try:
        user = await get_user(message.from_user.id)
        
        if message.text and message.text.startswith("/"):
            return

        if message.text:
            caption = message.text.html
        elif message.caption:
            caption = message.caption.html
            
        if len(await extract_link(caption)) <= 0 and not message.reply_markup:
            return
        user_method = user["method"]
        vld = await user_api_check(user)
        if vld is not True:
            return await message.reply_text(vld)
        try:
            txt = await message.reply(
                "`Cooking... It will take some time if you have enabled Link Bypass`",
                quote=True,
            )

            await main_convertor_handler(message, user=user)
            
            bin_caption = f"""{caption}\n\n#NewPost\nFrom User :- {message.from_user.mention} [`{message.from_user.id}`]"""

            try:
                if LOG_CHANNEL and message.media:
                    await message.copy(LOG_CHANNEL, bin_caption)
                elif message.text and LOG_CHANNEL:
                    await c.send_message(
                        LOG_CHANNEL, bin_caption, disable_web_page_preview=True
                    )
                
            except PeerIdInvalid as e:
                logging.error("Make sure that the bot is admin in your log channel")
            await update_stats(message, user_method)
        except Exception as e:
            await message.reply(f"Error while trying to convert links {e}:", quote=True)
            logger.exception(e)
        finally:
            await txt.delete()
    except Exception as e:
        logging.exception(e, exc_info=True)
