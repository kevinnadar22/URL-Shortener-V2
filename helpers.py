# temp db for banned 
import database
from config import ADMINS, CHANNEL_ID, CHANNELS, REPLIT, PING_INTERVAL

import asyncio
import logging
import aiohttp
import traceback

class temp(object): # TrojanZ Idea of Temping
    BOT_USERNAME = None
    CANCEL = False
    FIRST_NAME = None
    START_TIME = None
    BANNED_USERS = []

class AsyncIter:    
    def __init__(self, items):    
        self.items = items    

    async def __aiter__(self):    
        for item in self.items:    
            yield item  

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class Helpers:
    def __init__(self):
        self.username = temp.BOT_USERNAME

    @property
    async def user_method(self):
        user_method = await database.db.get_bot_method(self.username)
        if user_method:
            return user_method
        return "None"


    @property
    async def get_channels(self):
        x=''
        if CHANNELS:   
            async for i in AsyncIter(CHANNEL_ID):
                x+= f"~ `{i}`\n"
            return x
        return "Channels is set to False in heroku Var"

    @property
    async def get_admins(self):
        x=''
        async for i in AsyncIter(ADMINS):
            x+= f"~ `{i}`\n"
        return x

async def ping_server():
    sleep_time = PING_INTERVAL
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(REPLIT) as resp:
                    logging.info("Pinged server with response: {}".format(resp.status))
        except TimeoutError:
            logging.warning("Couldn't connect to the site URL..!")
        except Exception:
            traceback.print_exc()