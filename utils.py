from config import MDISK_KEY, DROPLINK_KEY, EXCLUDE_DOMAIN, INCLUDE_DOMAIN
import re
import aiohttp
import requests


####################  droplink  ####################


async def get_shortlink(link, x):
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)
        print(link)
    url = f'https://droplink.co/api'
    params = {'api': DROPLINK_KEY,
              'url': link,
              'alias': x
              }


    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
            data = await response.json()
            if data["status"] == "success":
                return data['shortenedUrl']
            else:
                return f"Error: {data['message']}"


async def replace_link(text, x):
    links = re.findall(r'https?://[^\s]+', text)
    for link in links:

        if INCLUDE_DOMAIN:
            include = INCLUDE_DOMAIN.split(',')
            domain = [domain.strip() for domain in include]
            if any(i in link for i in domain):
                short_link = await get_shortlink(link, x)
                text = text.replace(link, short_link)
                print(f"Included domain link: {link}")

        elif EXCLUDE_DOMAIN:
            exclude = EXCLUDE_DOMAIN.split(',')
            domain = [domain.strip() for domain in exclude]
            if any(i in link for i in domain):
                print(f"Excluded domain link: {link}")
                print(True, False)
            else:
                short_link = await get_shortlink(link, x)
                print(short_link)
                text = text.replace(link, short_link)

        else:
            short_link = await get_shortlink(link, x)
            print(short_link)
            text = text.replace(link, short_link)

    return text



####################  Mdisk  ####################


async def get_mdisk(link):
    url = 'https://diskuploader.mypowerdisk.com/v1/tp/cp'
    param = {'token': MDISK_KEY, 'link': link
             }
    res = requests.post(url, json=param)
    try:
        shareLink = res.json()
        link = shareLink["sharelink"]
    except:
        print(link, " is invalid")
    return link


async def replace_mdisk_link(text):
    links = re.findall(r'https?://mdisk.me[^\s]+', text)
    for link in links:
        mdisk_link = await get_mdisk(link)
        text = text.replace(link, mdisk_link)

    return text
