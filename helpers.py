# temp db for banned
import asyncio
import logging
import traceback

import aiohttp

import database
from config import ADMINS, CHANNEL_ID, CHANNELS, PING_INTERVAL, PORT


class temp(object):  # TrojanZ Idea of Temping
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
        except StopIteration as e:
            raise StopAsyncIteration from e


class Helpers:
    def __init__(self):
        self.username = temp.BOT_USERNAME

    @property
    async def user_method(self):
        user_method = await database.db.get_bot_method(self.username)
        return user_method or "None"

    @property
    async def get_channels(self):
        if CHANNELS:
            x = ""
            async for i in AsyncIter(CHANNEL_ID):
                x += f"~ `{i}`\n"
            return x
        return "Channels is set to False in heroku Var"

    @property
    async def get_admins(self):
        x = ""
        async for i in AsyncIter(ADMINS):
            x += f"~ `{i}`\n"
        return x


async def ping_server():
    sleep_time = PING_INTERVAL
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(f"http://0.0.0.0:{PORT}") as resp:
                    logging.info(f"Pinged server with response: {resp.status}")
        except TimeoutError:
            logging.warning("Couldn't connect to the site URL..!")
        except Exception:
            traceback.print_exc()
