from pyrogram import Client
from config import *
from helpers import temp



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
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        temp.BOT_USERNAME = me.username
        print(f"{self.username} running...")


    async def stop(self, *args):
        await super().stop()
        print("Bot stopped. Bye.")

