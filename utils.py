from ast import comprehension
import random
import string
from config import MDISK_API, DROPLINK_API, EXCLUDE_DOMAIN, INCLUDE_DOMAIN, USERNAME, REMOVE_EMOJI
import re
import aiohttp
import requests
####################  droplink  ####################


async def get_shortlink(link, x):
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)
    url = f'https://droplink/api'
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
        print(e)
        N = 6
        res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = N))
        links = f'[https://droplink.co/{res}](https://droplink.co/st?api={DROPLINK_API}&url={link})'
        return links


async def replace_link(text, x):
    text = await replace_username(text)
    text = await remove_emoji(text)
    links = re.findall(r'https?://[^\s]+', str(text))
    for link in links:

        if INCLUDE_DOMAIN:
            include = INCLUDE_DOMAIN.split(',')
            domain = [domain.strip() for domain in include]
            if any(i in link for i in domain):
                short_link = await get_shortlink(link, x)
                text = text.replace(link, short_link)


        elif EXCLUDE_DOMAIN:
            exclude = EXCLUDE_DOMAIN.split(',')
            domain = [domain.strip() for domain in exclude]
            if any(i in link for i in domain):
                pass
            else:
                short_link = await get_shortlink(link, x)

                text = text.replace(link, short_link)

        else:
            short_link = await get_shortlink(link, x)

            text = text.replace(link, short_link)

    return text



####################  Mdisk  ####################

async def get_mdisk(link):
    url = 'https://diskuploader.mypowerdisk.com/v1/tp/cp'
    param = {'token': MDISK_API, 'link': link
             }
    res = requests.post(url, json=param)
    try:
        shareLink = res.json()
        link = shareLink["sharelink"]
    except:
        pass
    return link


async def replace_mdisk_link(text):
    text = await replace_username(text)
    text = await remove_emoji(text)
    links = re.findall(r'https?://mdisk.me[^\s]+', str(text))
    for link in links:
        mdisk_link = await get_mdisk(link)
        text = text.replace(link, mdisk_link)

    return text


####################  Mdisk and Droplink  ####################

async def mdisk_droplink_convertor(text):
    links = await replace_mdisk_link(text)
    links = await replace_link(links, x="")
    links = await replace_username(links)
    links = await remove_emoji(links)
    return links


####################  Replace Username  ####################


async def replace_username(text):
    usernames = re.findall("([@#][A-Za-z0-9_]+)", str(text))

    for i in usernames:
        text = text.replace(i, f"@{USERNAME}")

    telegram_links = re.findall(r'[(?:http|https)?://]*(?:t.me|telegram.me|telegram.dog)[^\s]+', str(text))

    for i in telegram_links:
        text = text.replace(i, f"@{USERNAME}")

    return text

#####################  Remove Emojis ####################
async def remove_emoji(string):
    if REMOVE_EMOJI:
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub('', string)
    else:
        return string


