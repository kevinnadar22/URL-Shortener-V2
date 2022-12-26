import json
import logging
import re
from urllib.parse import urlparse

import aiohttp
import heroku3
from mdisky import Mdisk
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)
from shortzy import Shortzy

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from config import *
from database import db
import PyBypass as bypasser

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1000)


async def main_convertor_handler(
    message: Message, type: str, edit_caption: bool = False, user=None
):
    """
    This function is used to convert a message to a different format

    :param message: The message object that the user sent
    :type message: Message
    :param type: str - The type of the media to be converted
    :type type: str
    :param edit_caption: If you want to edit the caption of the message, set this to True, defaults to
    False
    :type edit_caption: bool (optional)
    :param user: The user who sent the message
    """
    if user:
        header_text = (
            user["header_text"].replace(r"\n", "\n") if user["is_header_text"] else ""
        )
        footer_text = (
            user["footer_text"].replace(r"\n", "\n") if user["is_footer_text"] else ""
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
            return await message.edit(
                shortenedText, disable_web_page_preview=True, reply_markup=reply_markup
            )

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

            return await message.edit_caption(
                shortenedText, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )

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
                text = button_data["text"]
                url = await method_func(user=user, text=button_data["url"])
                row_buttons.append(InlineKeyboardButton(text, url=url))
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
    reply_markup = str(m.reply_markup) if m.reply_markup else ""
    message = m.caption.html if m.caption else m.text.html
    mdisk_links = re.findall(
        r'https?://mdisk.me[^\s`!()\[\]{};:".,<>?«»“”‘’]+', message + reply_markup
    )
    droplink_links = await extract_link(message + reply_markup)
    total_links = len(droplink_links)
    await db.update_posts(1)
    if method == "mdisk":
        droplink_links = []
    if method == "shortener":
        mdisk_links = []
    await db.update_links(total_links, len(droplink_links), len(mdisk_links))


async def TimeFormatter(milliseconds) -> str:
    milliseconds = int(milliseconds) * 1000
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{str(days)}d, " if days else "")
        + (f"{str(hours)}h, " if hours else "")
        + (f"{str(minutes)}m, " if minutes else "")
        + (f"{str(seconds)}s, " if seconds else "")
        + (f"{str(milliseconds)}ms, " if milliseconds else "")
    )

    return tmp[:-2]


async def getHerokuDetails(h_api_key, h_app_name):
    if not h_api_key or not h_app_name:
        logger.info("if you want heroku dyno stats, read readme.")
        return None
    try:
        heroku_api = "https://api.heroku.com"
        Heroku = heroku3.from_key(h_api_key)
        app = Heroku.app(h_app_name)
        useragent = user_agent_rotator.get_random_user_agent()
        user_id = Heroku.account().id
        headers = {
            "User-Agent": useragent,
            "Authorization": f"Bearer {h_api_key}",
            "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }

        path = f"/accounts/{user_id}/actions/get-quota"
        async with aiohttp.ClientSession() as session:
            result = await session.get(heroku_api + path, headers=headers)
        result = await result.json()
        abc = ""
        account_quota = result["account_quota"]
        quota_used = result["quota_used"]
        quota_remain = account_quota - quota_used
        abc += f"<b>- Dyno Used:</b> `{await TimeFormatter(quota_used)}`\n"
        abc += f"<b>- Free:</b> `{await TimeFormatter(quota_remain)}`\n"
        AppQuotaUsed = 0
        OtherAppsUsage = 0
        for apps in result["apps"]:
            if str(apps.get("app_uuid")) == str(app.id):
                try:
                    AppQuotaUsed = apps.get("quota_used")
                except Exception as t:
                    logger.error("error when adding main dyno")
                    logger.error(t)
            else:
                try:
                    OtherAppsUsage += int(apps.get("quota_used"))
                except Exception as t:
                    logger.error("error when adding other dyno")
                    logger.error(t)
        logger.info(f"This App: {str(app.name)}")
        abc += f"<b>- This App:</b> `{await TimeFormatter(AppQuotaUsed)}`\n"
        abc += f"<b>- Other:</b> `{await TimeFormatter(OtherAppsUsage)}`"
        return abc
    except Exception as g:
        logger.error(g)
        return None


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
    text = ""
    if user_method in ["mdisk", "mdlink"] and not user["mdisk_api"]:
        text += "\n\nSet your /mdisk_api to continue..."
    if user_method in ["shortener", "mdlink"] and not user["shortener_api"]:
        text += f"\n\nSet your /shortener_api to continue...\nCurrent Website {user['base_site']}"

    if not user_method:
        text = "\n\nSet your /method first"
    return text or True


def extract_domain(link):
    parsed_url = urlparse(link)
    return parsed_url.netloc