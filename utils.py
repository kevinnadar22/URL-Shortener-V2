import asyncio
import json
import logging
import random
import re
from urllib.parse import urlparse

import aiohttp
import heroku3
from bs4 import BeautifulSoup
from mdisky import Mdisk
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InputMediaPhoto, Message)
from shortzy import Shortzy

from config import *
from database import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def main_convertor_handler(message:Message, type:str, edit_caption:bool=False, user=None):
    if user:
        header_text = user["header_text"].replace(r'\n', '\n') if user["is_header_text"] else ""
        footer_text = user["footer_text"].replace(r'\n', '\n') if user["is_footer_text"] else ""
        username = user["username"] if user["is_username"] else None
        banner_image = user["banner_image"] if user["is_banner_image"] else None

    caption = None

    if message.text:
        caption = message.text.html
    elif message.caption:
        caption = message.caption.html

    # Checking if the message has any link or not. If it doesn't have any link, it will return.
    if len(await extract_link(caption)) <=0 and not message.reply_markup:
        return

    user_method = user["method"]

    # Checking if the user has set his method or not. If not, it will reply with a message.
    if user_method is None:
        return await message.reply(text="Set your /method first")

    # Bypass Links
    caption = await droplink_bypass_handler(caption)

    # A dictionary which contains the methods to be called.
    METHODS = {
        "mdisk": mdisk_api_handler,
        "shortener": replace_link,
        "mdlink": mdisk_droplink_convertor
    }

    # Replacing the username with your username.
    caption = await replace_username(caption, username)

    # Getting the function for the user's method
    method_func = METHODS[user_method] 

    # converting urls
    shortenedText = await method_func(user, caption)

    # converting reply_markup urls
    reply_markup = await reply_markup_handler(message, method_func, user=user)

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
        if user_method in ["shortener", "mdlink"] and '|' in caption:
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))\s\|\s([a-zA-Z0-9_]){,30}"
            if custom_alias := re.match(regex, caption):
                custom_alias = custom_alias[0].split('|')
                alias = custom_alias[1].strip()
                url = custom_alias[0].strip()
                shortenedText = await method_func(user, url, alias=alias)

        if edit_caption:
            return await message.edit(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup)

        return await message.reply(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup, quote=True, parse_mode=ParseMode.HTML)

    elif message.media:

        if edit_caption:
            if banner_image and message.photo:
                return await message.edit_media(media=fileid)

            return await message.edit_caption(shortenedText, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

        if message.document:
            return await message.reply_document(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True, parse_mode=ParseMode.HTML)


        elif message.photo:
            return await message.reply_photo(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True, parse_mode=ParseMode.HTML)


# Reply markup 
async def reply_markup_handler(message:Message, method_func, user):
    if message.reply_markup:
        reply_markup = json.loads(str(message.reply_markup))
        buttsons = []
        for markup in reply_markup["inline_keyboard"]:
            buttons = []
            for j in markup:
                text = j["text"]
                url = j["url"]
                url = await method_func(user=user, text=url)
                button = InlineKeyboardButton(text, url=url)
                buttons.append(button)
            buttsons.append(buttons)
        reply_markup = InlineKeyboardMarkup(buttsons)
        return reply_markup


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
        https = link.split(":")[0]
        if https == "http":
            https = "https"
            link = link.replace("http", https)
        long_url = link
        if user["include_domain"]:
            include = user["include_domain"]
            domain = [domain.strip() for domain in include]
            if any(i in link for i in domain):
                short_link = await shortzy.convert(link, alias)
                text = text.replace(long_url, short_link)
        elif user["exclude_domain"]:
            exclude = user["exclude_domain"]
            domain = [domain.strip() for domain in exclude]
            if all(i not in link for i in domain):
                short_link = await shortzy.convert(link, alias)
                text = text.replace(long_url, short_link)
        else:
            short_link = await shortzy.convert(link, alias)
            text = text.replace(long_url, short_link)
    return text

# Mdisk and Droplink  
async def mdisk_droplink_convertor(user, text, alias=""):
    links = await mdisk_api_handler(user, text)
    links = await replace_link(user, links, alias=alias)
    return links

# Replace Username  
async def replace_username(text, username):
    if username:
        usernames = re.findall("([@][A-Za-z0-9_]+)", text)
        for i in usernames:
            text = text.replace(i, f"@{username}")
    return text
    
# Extract all urls in a string 
async def extract_link(string):
    regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    urls = re.findall(regex, string)
    return ["".join(x) for x in urls]

# todo -> bypass long droplink url
async def droplink_bypass_handler(text):
    if LINK_BYPASS:
        links = re.findall(r'https?://droplink.co[^\s"*<>`()]+', text)	
        for link in links:
            bypassed_link = await droplink_bypass(link)
            text = text.replace(link, bypassed_link)
    return text

# credits -> https://github.com/TheCaduceus/Link-Bypasser
async def droplink_bypass(url):  
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as res:
                ref = re.findall("""action[ ]{0,}=[ ]{0,}['|\"](.*?)['|\"]""", await res.text())[0]
                h = {'referer': ref}
                async with client.get(url, headers=h) as res:
                    bs4 = BeautifulSoup(await res.content.read(), 'html.parser')
                    inputs = bs4.find_all('input')
                    data = {input.get('name'): input.get('value') for input in inputs}
                    h = {'content-type': 'application/x-www-form-urlencoded', 'x-requested-with': 'XMLHttpRequest'}
                    p = urlparse(url)
                    final_url = f'{p.scheme}://{p.netloc}/links/go'
                    await asyncio.sleep(3.1)
                    async with client.post(final_url, data=data, headers=h) as res:
                        res = await res.json()
                        return res['url'] if res['status'] == 'success' else res['message']
    except Exception as e:
        raise Exception("Error while bypassing droplink {0}: {1}".format(url, e)) from e

async def is_droplink_url(url):
    domain = urlparse(url).netloc
    domain = url if "droplink.co" in domain else False
    return domain


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

async def update_stats(m:Message, method):
    reply_markup = str(m.reply_markup) if m.reply_markup else ''
    message = m.caption.html if m.caption else m.text.html
    mdisk_links = re.findall(r'https?://mdisk.me[^\s`!()\[\]{};:".,<>?«»“”‘’]+', message + reply_markup)
    droplink_links = await extract_link(message + reply_markup)
    total_links = len(droplink_links)
    await db.update_posts(1)
    if method == 'mdisk': droplink_links = []
    if method == 'shortener': mdisk_links = []
    await db.update_links(total_links, len(droplink_links), len(mdisk_links))


#  Heroku Stats
async def getRandomUserAgent():
    agents = [
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.699.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.220 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (X11; CrOS i686 0.13.507) AppleWebKit/534.35 (KHTML, like Gecko) Chrome/13.0.763.0 Safari/534.35",
    "Mozilla/5.0 (X11; CrOS i686 0.13.587) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.14 Safari/535.1",
    "Mozilla/5.0 (X11; CrOS i686 1193.158.0) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7",
    "Mozilla/5.0 (X11; CrOS i686 12.0.742.91) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.93 Safari/534.30",
    "Mozilla/5.0 (X11; CrOS i686 12.433.109) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.93 Safari/534.30",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.34 Safari/534.24",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.04 Chromium/11.0.696.0 Chrome/11.0.696.0 Safari/534.24",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.703.0 Chrome/12.0.703.0 Safari/534.24",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21",
    "Opera/9.80 (Windows NT 5.1; U; sk) Presto/2.5.22 Version/10.50",
    "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00",
    "Opera/9.80 (Windows NT 5.1; U; zh-tw) Presto/2.8.131 Version/11.10",
    "Opera/9.80 (Windows NT 5.1; U;) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (Windows NT 5.2; U; en) Presto/2.6.30 Version/10.63",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.6.30 Version/10.61",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (X11; Linux x86_64; U; pl) Presto/2.7.62 Version/11.00",
    "Opera/9.80 (X11; Linux x86_64; U; Ubuntu/10.10 (maverick); pl) Presto/2.7.62 Version/11.01",
    "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.117 Mobile Safari/537.36"
    ]
    return agents[random.randint(0, len(agents)-1)]


async def TimeFormatter(milliseconds) -> str:
    milliseconds = int(milliseconds) * 1000
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (f"{str(days)}d, " if days else "") + (f"{str(hours)}h, " if hours else "") + (f"{str(minutes)}m, " if minutes else "") + (f"{str(seconds)}s, " if seconds else "") + (f"{str(milliseconds)}ms, " if milliseconds else "")

    return tmp[:-2]


async def getHerokuDetails(h_api_key, h_app_name):
    if not h_api_key or not h_app_name:
        logger.info("if you want heroku dyno stats, read readme.")
        return None
    try:
        heroku_api = "https://api.heroku.com"
        Heroku = heroku3.from_key(h_api_key)
        app = Heroku.app(h_app_name)
        useragent = await getRandomUserAgent()
        user_id = Heroku.account().id
        headers = {"User-Agent": useragent, "Authorization": f"Bearer {h_api_key}", "Accept": "application/vnd.heroku+json; version=3.account-quotas"}

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
        buttons = [[InlineKeyboardButton('Header Text', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_header_text"] else '✅ Enable', callback_data=f'setgs#is_header_text#{not user["is_header_text"]}#{str(user_id)}')], [InlineKeyboardButton('Footer Text', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_footer_text"] else '✅ Enable', callback_data=f'setgs#is_footer_text#{not user["is_footer_text"]}#{str(user_id)}')], [InlineKeyboardButton('Username', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_username"] else '✅ Enable', callback_data=f'setgs#is_username#{not user["is_username"]}#{str(user_id)}')], [InlineKeyboardButton('Banner Image', callback_data='ident'), InlineKeyboardButton('❌ Disable' if user["is_banner_image"] else '✅ Enable', callback_data=f'setgs#is_banner_image#{not user["is_banner_image"]}#{str(user_id)}')]]
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
