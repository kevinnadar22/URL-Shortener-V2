import asyncio
import json
import logging
import re
import sys
from urllib.parse import urlparse

import PyBypass as bypasser
from aiohttp import web
from mdisky import Mdisk
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, MessageNotModified, PeerIdInvalid
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InputMediaPhoto, Message, BotCommand)
from shortzy import Shortzy

from config import *
from database import db
from helpers import ping_server
from plugins import web_server

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def main_convertor_handler(
    message: Message, edit_caption: bool = False, user=None
):

    """
    This function is used to convert a message to a different format

    :param message: The message object that the user sent
    :type message: Message
    :param type: str - The type of the media to be converted
    :param edit_caption: If you want to edit the caption of the message, set this to True, defaults to
    False
    :type edit_caption: bool (optional)
    :param user: The user who sent the message
    """
    if user:
        header_text = (
            user["header_text"].replace(
                r"\n", "\n") if user["is_header_text"] else ""
        )
        footer_text = (
            user["footer_text"].replace(
                r"\n", "\n") if user["is_footer_text"] else ""
        )
        username = user["username"] if user["is_username"] else None
        banner_image = user["banner_image"] if user["is_banner_image"] else None

    caption = None

    if message.text:
        caption = message.text.html
    elif message.caption:
        caption = message.caption.html

    # Checking if the message has any link or not. If it doesn't have any link, it will return.
    if len(await extract_link(caption)) <= 0 and not message.reply_markup:
        return

    user_method = user["method"]

    # Checking if the user has set his method or not. If not, it will reply with a message.
    if user_method is None:
        return await message.reply(text="Set your /method first")

    # Bypass Links
    caption = await bypass_handler(caption)

    # A dictionary which contains the methods to be called.
    METHODS = {
        "mdisk": mdisk_api_handler,
        "shortener": replace_link,
        "mdlink": mdisk_droplink_convertor,
    }

    # Replacing the username with your username.
    caption = await replace_username(caption, username)

    # Getting the function for the user's method
    method_func = METHODS[user_method]

    # converting urls
    shortenedText = await method_func(user, caption)

    # converting reply_markup urls
    reply_markup = await create_inline_keyboard_markup(message, method_func, user=user)

    # Adding header and footer
    shortenedText = f"{header_text}\n{shortenedText}\n{footer_text}"

    # Used to get the file_id of the media. If the media is a photo and BANNER_IMAGE is set, it will
    # replace the file_id with the BANNER_IMAGE.
    if message.media:
        medias = getattr(message, message.media.value)
        fileid = medias.file_id
        if message.photo and banner_image:
            fileid = banner_image
            if edit_caption:
                fileid = InputMediaPhoto(banner_image, caption=shortenedText)

    if message.text:
        if user_method in ["shortener", "mdlink"] and "|" in caption:
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))\s\|\s([a-zA-Z0-9_]){,30}"
            if custom_alias := re.match(regex, caption):
                custom_alias = custom_alias[0].split("|")
                alias = custom_alias[1].strip()
                url = custom_alias[0].strip()
                shortenedText = await method_func(user, url, alias=alias)

        if edit_caption:
            try:
                return await message.edit(
                    shortenedText, disable_web_page_preview=True, reply_markup=reply_markup
                )
            except MessageNotModified:
                return

        return await message.reply(
            shortenedText,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True,
            parse_mode=ParseMode.HTML,
        )

    elif message.media:
        if edit_caption:
            if banner_image and message.photo:
                return await message.edit_media(media=fileid)

            try:
                await message.edit_caption(
                    shortenedText, reply_markup=reply_markup, parse_mode=ParseMode.HTML
                )
                return
            except MessageNotModified:
                return

        meta = {
            "caption": shortenedText,
            "reply_markup": reply_markup,
            "quote": True,
            "parse_mode": ParseMode.HTML,
        }
        if message.document:
            return await message.reply_document(document=fileid, **meta)

        elif message.photo:
            return await message.reply_photo(photo=fileid, **meta)

        elif message.video:
            return await message.reply_video(video=fileid, **meta)


async def create_inline_keyboard_markup(message: Message, method_func, user):
    if message.reply_markup:
        reply_markup = json.loads(str(message.reply_markup))
        buttons = []


        for markup in reply_markup["inline_keyboard"]:
            row_buttons = []
            for button_data in markup:
                if button_data.get("url"):
                    text = button_data["text"]
                    url = await method_func(user=user, text=button_data["url"])
                    row_buttons.append(InlineKeyboardButton(text, url=url))
                elif button_data.get("callback_data"):
                    row_buttons.append(InlineKeyboardButton(text=button_data["text"], callback_data=button_data["callback_data"]))
                else:
                    row_buttons.append(InlineKeyboardButton(text=button_data["text"], switch_inline_query_current_chat=button_data["switch_inline_query_current_chat"]))

            buttons.append(row_buttons)
        return InlineKeyboardMarkup(buttons)


async def mdisk_api_handler(user, text, alias=""):
    api_key = user["mdisk_api"]
    mdisk = Mdisk(api_key)
    return await mdisk.convert_from_text(text)


async def replace_link(user, text, alias=""):
    api_key = user["shortener_api"]
    base_site = user["base_site"]
    shortzy = Shortzy(api_key, base_site)
    links = await extract_link(text)

    for link in links:
        if not link.startswith("https:"):
            link = link.replace("http:", "https:", 1)
        long_url = link

        should_replace_link = False
        if user["include_domain"]:
            include = user["include_domain"]
            domains = [domain.strip() for domain in include]
            if any(i in link for i in domains):
                should_replace_link = True
        elif user["exclude_domain"]:
            exclude = user["exclude_domain"]
            domains = [domain.strip() for domain in exclude]
            if all(i not in link for i in domains):
                should_replace_link = True
        else:
            should_replace_link = True

        if should_replace_link:
            short_link = await shortzy.convert(link, alias)
            text = text.replace(long_url, short_link)

    return text


async def mdisk_droplink_convertor(user, text, alias=""):
    links = await mdisk_api_handler(user, text)
    links = await replace_link(user, links, alias=alias)
    return links


async def replace_username(text, username):
    if username:
        usernames = re.findall(r"@[A-Za-z0-9_]+", text)
        for old_username in usernames:
            text = text.replace(old_username, f"@{username}")
    return text


async def extract_link(string):
    regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    urls = re.findall(regex, string)
    return ["".join(x) for x in urls]


async def bypass_handler(text):
    if LINK_BYPASS:
        links = await extract_link(text)
        for link in links:
            domain = extract_domain(link)
            if domain not in DE_BYPASS:
                bypassed_link = await bypass_func(link)
                text = text.replace(link, bypassed_link)
    return text


async def bypass_func(url):
    try:
        c_link = bypasser.bypass(url)
    except Exception:
        c_link = url
    return c_link


async def is_droplink_url(url):
    domain = urlparse(url).netloc
    return url if "droplink.co" in domain else False


async def broadcast_admins(c: Client, Message, sender=False):
    admins = ADMINS[:]
    if sender:
        admins.remove(sender)
    for i in admins:
        try:
            await c.send_message(i, Message)
        except PeerIdInvalid:
            logging.info(f"{i} have not yet started the bot")
        except FloodWait as e:
            logging.error(f"Sleeping for {e.x} seconds")
            await asyncio.sleep(e.x)
        except:
            logging.error(f"Unexpected error: {sys.exc_info()[0]}")
    return


async def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


async def update_stats(m: Message, method):
    if m.caption:
        message = m.caption.html
    else:
        message = m.text.html

    mdisk_links = re.findall(
        r'https?://mdisk.me[^\s`!()\[\]{};:".,<>?«»“”‘’]+', message
    )
    droplink_links = await extract_link(message)
    total_links = len(droplink_links)
    await db.update_posts(1)
    if method == "mdisk":
        droplink_links = []
    if method == "shortener":
        mdisk_links = []
    await db.update_links(total_links, len(droplink_links), len(mdisk_links))


async def get_me_button(user):
    user_id = user["user_id"]
    buttons = []
    try:
        buttons = [
            [
                InlineKeyboardButton("Header Text", callback_data="ident"),
                InlineKeyboardButton(
                    "❌ Disable" if user["is_header_text"] else "✅ Enable",
                    callback_data=f'setgs#is_header_text#{not user["is_header_text"]}#{str(user_id)}',
                ),
            ],
            [
                InlineKeyboardButton("Footer Text", callback_data="ident"),
                InlineKeyboardButton(
                    "❌ Disable" if user["is_footer_text"] else "✅ Enable",
                    callback_data=f'setgs#is_footer_text#{not user["is_footer_text"]}#{str(user_id)}',
                ),
            ],
            [
                InlineKeyboardButton("Username", callback_data="ident"),
                InlineKeyboardButton(
                    "❌ Disable" if user["is_username"] else "✅ Enable",
                    callback_data=f'setgs#is_username#{not user["is_username"]}#{str(user_id)}',
                ),
            ],
            [
                InlineKeyboardButton("Banner Image", callback_data="ident"),
                InlineKeyboardButton(
                    "❌ Disable" if user["is_banner_image"] else "✅ Enable",
                    callback_data=f'setgs#is_banner_image#{not user["is_banner_image"]}#{str(user_id)}',
                ),
            ],
        ]
    except Exception as e:
        print(e)
    return buttons


async def user_api_check(user):
    user_method = user["method"]
    if user_method == "mdisk":
        if not user["mdisk_api"]:
            return "\n\nSet your /mdisk_api to continue..."
    elif user_method == "shortener":
        if not user["shortener_api"]:
            return f"\n\nSet your /shortener_api to continue...\nCurrent Website {user['base_site']}"
    elif user_method == "mdlink":
        if not user["mdisk_api"]:
            return "\n\nSet your /mdisk_api to continue..."
        if not user["shortener_api"]:
            return f"\n\nSet your /shortener_api to continue...\nCurrent Website {user['base_site']}"
    else:
        return "\n\nSet your /method first"
    return True


def extract_domain(link):
    parsed_url = urlparse(link)
    return parsed_url.netloc


async def create_server():
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()
    asyncio.create_task(ping_server())


async def set_commands(app):
    COMMANDS = [
        BotCommand("start", "Used to start the bot."),
        BotCommand("help", "Displays the help command."),
        BotCommand("about", "Displays information about the bot."),
        BotCommand("method", "Sets your preferred method."),
        BotCommand("shortener_api", "Sets the shortener API."),
        BotCommand("mdisk_api", "Sets the mDisk API."),
        BotCommand("header", "Sets the header."),
        BotCommand("footer", "Sets the footer."),
        BotCommand("username", "Sets the username to replace others."),
        BotCommand("banner_image", "Sets the banner image."),
        BotCommand("me", "Displays information about the bot."),
        BotCommand("base_site", "Changes the base site."),
        BotCommand("include_domain", "Sets the included domain."),
        BotCommand("exclude_domain", "Sets the excluded domain."),
        BotCommand("stats", "Displays statistics of the server and bot."),
        BotCommand("batch", "Converts link for multiple posts (admin only)."),
        BotCommand("logs", "Sends the log messages (admin only)."),
        BotCommand("restart", "Restarts or re-deploys the server (admin only)."),
        BotCommand("ban", "Bans users (admin only)."),
        BotCommand("unban", "Unbans users (admin only)."),
        BotCommand("info", "Gets user info (admin only)."),
    ]

    await app.set_bot_commands(COMMANDS)
