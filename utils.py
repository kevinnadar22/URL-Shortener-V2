import asyncio
import re
import json
import aiohttp
from pyrogram import Client



from mdisky import Mdisk
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urlparse

from config import *
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyshorteners
from pyrogram.types import InputMediaPhoto

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


mdisk = Mdisk(MDISK_API)

async def main_convertor_handler(message:Message, type:str, edit_caption:bool=False):
    caption = None


    if message.text:
        caption = message.text.html
    elif message.caption:
        caption = message.caption.html


    # Checking if the message has any link or not. If it doesn't have any link, it will return.
    if len(await extract_link(caption)) <=0 and not message.reply_markup:
        return

    user_method = type

    # Checking if the user has set his method or not. If not, it will reply with a message.
    if user_method is None:
        return await message.reply(text="Set your /method first")

    # A dictionary which contains the methods to be called.
    METHODS = {
        "mdisk": replace_mdisk_link,
        "droplink": replace_link,
        "mdlink": mdisk_droplink_convertor
    }

    # Replacing the username with your username.
    caption = await replace_username(caption)


    # Getting the function for the user's method
    method_func = METHODS[user_method] 

    # converting urls
    shortenedText = await method_func(caption)

    # converting reply_markup urls
    reply_markup = await reply_markup_handler(message, method_func)

    # Adding header and footer
    shortenedText = f"{HEADER_TEXT}\n{shortenedText}\n{FOOTER_TEXT}"


    # Used to get the file_id of the media. If the media is a photo and BANNER_IMAGE is set, it will
    # replace the file_id with the BANNER_IMAGE.
    if message.media:
        medias = getattr(message, message.media.value)
        fileid = medias.file_id
        if message.photo and BANNER_IMAGE:
            fileid = BANNER_IMAGE
            if edit_caption:
                fileid = InputMediaPhoto(BANNER_IMAGE, caption=shortenedText)
        

    if message.text:
        if user_method in ["droplink", "mdlink"] :
            if '|' not in caption:
                pass
            else:
                regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))\s\|\s([a-zA-Z0-9_]){,30}"
                custom_alias = re.match(regex, caption)

                if custom_alias:
                    custom_alias = custom_alias.group(0).split('|')
                    alias = custom_alias[1].strip()
                    url = custom_alias[0].strip()
                    shortenedText = await method_func(url, alias)
        
        if edit_caption:
            return await message.edit(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup)

        return await message.reply(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup, quote=True)

    elif message.media:

        if edit_caption:
            if BANNER_IMAGE and message.photo:
                return await message.edit_media(media=fileid)

            return await message.edit_caption(shortenedText, reply_markup=reply_markup)

        if message.document:
            return await message.reply_document(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True)

        
        elif message.photo:
            return await message.reply_photo(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True)



# Reply markup 
async def reply_markup_handler(message:Message, method_func):
    if message.reply_markup:
        reply_markup = json.loads(str(message.reply_markup))
        buttsons = []
        for markup in reply_markup["inline_keyboard"]:
            buttons = []
            for j in markup:
                text = j["text"]
                url = j["url"]
                url = await method_func(url)
                button = InlineKeyboardButton(text, url=url)
                buttons.append(button)
            buttsons.append(buttons)
        reply_markup = InlineKeyboardMarkup(buttsons)
        return reply_markup


####################  droplink  ####################
async def get_shortlink(link, x=""):
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)

    url = f'https://droplink.co/api'
    params = {'api': DROPLINK_API,
              'url': link,
              'alias': x
              }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                data = await response.json()
                if data["status"] == "success":
                    return data['shortenedUrl']
                else:
                    return f"Error: {data['message']}"

    except Exception as e:
        logger.error(e)
        links = f'https://droplink.co/st?api={DROPLINK_API}&url={link}'
        return await tiny_url_main(links)


async def replace_link(text, x=""):
    links = await extract_link(text)

    for link in links:

        long_url = link
        
        # Link Bypass Configuration
        droplink_url = await is_droplink_url(link)  

        if LINK_BYPASS and droplink_url or not droplink_url:
            # Bypass Droplink URL
            if LINK_BYPASS and droplink_url:
                try:
                    link = await droplink_bypass(link)
                except Exception as e:
                    logger.exception(e)

            # Include domain validation 
            if INCLUDE_DOMAIN:
                include = INCLUDE_DOMAIN
                domain = [domain.strip() for domain in include]
                if any(i in link for i in domain):
                    short_link = await get_shortlink(link, x)
                    text = text.replace(long_url, short_link)

            # Exclude domain validation 
            elif EXCLUDE_DOMAIN:
                exclude = EXCLUDE_DOMAIN
                domain = [domain.strip() for domain in exclude]
                if any(i in link for i in domain):
                    pass
                else:
                    short_link = await get_shortlink(link, x)
                    text = text.replace(long_url, short_link)

            # if not include domain and exlude domain
            else:
                short_link = await get_shortlink(link, x)
                text = text.replace(long_url, short_link)
    return text


####################  Mdisk  ####################

async def replace_mdisk_link(text):
    text = await mdisk.convert_from_text(text, True)
    return text


####################  Mdisk and Droplink  ####################

async def mdisk_droplink_convertor(text, alias=""):
    links = await replace_mdisk_link(text)
    links = await replace_link(links, x=alias)
    return links

####################  Mdisk and Droplink Reply Markup ####################

async def mdisk_droplink_convertor_reply_markup(text):
    links = await replace_mdisk_link(text)
    links = await replace_link(links, x="")
    return links

####################  Replace Username  ####################
async def replace_username(text):
    if USERNAME:
        usernames = re.findall("([@#][A-Za-z0-9_]+)", text)
        for i in usernames:
            text = text.replace(i, f"@{USERNAME}")
    return text
    

#####################  Extract all urls in a string ####################
async def extract_link(string):
    regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    urls = re.findall(regex, string)
    return ["".join(x) for x in urls]


# Incase droplink server fails, bot will return https://droplink.co/st?api={DROPLINK_API}&url={link} 

# TinyUrl 
async def tiny_url_main(url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)

# todo -> bypass long droplink url
async def droplink_bypass_handler(text):
    links = re.findall(r'https?://droplink.co[^\s"*<>]+', text)	
    for link in links:
        bypassed_link = await droplink_bypass(link)
        text = text.replace(link, bypassed_link)

    return text


# credits -> https://github.com/TheCaduceus/Link-Bypasser
async def droplink_bypass(url):
    try:
        # client = aiohttp.ClientSession()
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as res:
                
                ref = re.findall("action[ ]{0,}=[ ]{0,}['|\"](.*?)['|\"]", await res.text())[0]

                h = {'referer': ref}

                # res = client.get(url, headers=h)
                async with client.get(url, headers=h) as res:


                    bs4 = BeautifulSoup(await res.content.read(), 'html.parser')

                    inputs = bs4.find_all('input')
                    
                    data = { input.get('name'): input.get('value') for input in inputs }

                    h = {
                        'content-type': 'application/x-www-form-urlencoded',
                        'x-requested-with': 'XMLHttpRequest'
                    }
                    p = urlparse(url)
                    final_url = f'{p.scheme}://{p.netloc}/links/go'

                    await asyncio.sleep(3.1)

                    # res = client.post(final_url, data=data, headers=h).json()
                    async with client.post(final_url, data=data, headers=h) as res:

                        res = await res.json()

                        if res['status'] == 'success':
                            return res['url']
                        else:
                            raise Exception("Error while bypassing droplink {0}: {1}".format(url, res['message']))
            await client.close()

    except Exception as e:
        raise Exception("Error while bypassing droplink {0}: {1}".format(url, e))


async def is_droplink_url(url):
    domain = urlparse(url).netloc
    domain = url if "droplink.co" in domain else False
    return domain


async def broadcast_admins(c: Client, Message, sender=False):

    admins = ADMINS[:]
    
    if sender:
        admins.remove(sender)

    for i in admins:
        await c.send_message(i, Message)
    return