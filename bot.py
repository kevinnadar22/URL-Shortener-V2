from pyrogram import Client
from config import *


class Bot:
    bot = Client(
        "shortener",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")

    )

