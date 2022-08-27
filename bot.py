import asyncio
import datetime
import logging
import logging.config
import sys

from pyrogram import Client
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate

from config import *
from database import db
from database.users import filter_users
from helpers import ping_server, temp
from utils import broadcast_admins

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)


if REPLIT:
    from threading import Thread

    from flask import Flask, jsonify
    
    app = Flask('')
    
    @app.route('/')
    def main():
        
        runtime = datetime.datetime.now()
        t = runtime - temp.START_TIME
        runtime = str(datetime.timedelta(seconds=t.seconds))
        
        res = {
            "status":"running",
            "hosted":"replit.com",
            "repl":REPLIT,
            "bot":temp.BOT_USERNAME,
            "runtime":runtime
        }
        
        return jsonify(res)

    def run():
      app.run(host="0.0.0.0", port=8000)
    
    async def keep_alive():
      server = Thread(target=run)
      server.start()


class Bot(Client):

    def __init__(self):
        super().__init__(
        "shortener",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
        )

    async def start(self):
        if REPLIT:
            await keep_alive()
            asyncio.create_task(ping_server())
        temp.START_TIME = datetime.datetime.now()
        await super().start()
        
        if UPDATE_CHANNEL:
            try:
                self.invite_link = await self.create_chat_invite_link(UPDATE_CHANNEL)
            except Exception:
                logging.error(f"Make sure to make the bot in your update channel {UPDATE_CHANNEL}")
                sys.exit(1)

        me = await self.get_me()
        self.owner = await self.get_users(int(OWNER_ID))
        self.username = f'@{me.username}'
        temp.BOT_USERNAME = me.username
        temp.FIRST_NAME = me.first_name
        if not await db.get_bot_stats():
            await db.create_stats()
        banned_users = await filter_users({"banned": True})
        async for user in banned_users:
            temp.BANNED_USERS.append(user["user_id"])
        logging.info(LOG_STR)
        await broadcast_admins(self, '** Bot started successfully **')
        logging.info('Bot started')

    async def stop(self, *args):
        await broadcast_admins(self, '** Bot Stopped Bye **')
        await super().stop()
        logging.info('Bot Stopped Bye')

