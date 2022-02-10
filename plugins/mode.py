from pyrogram import Client, filters
from config import MODE


@Client.on_message(filters.command('mode') & filters.private)
async def mode_message(c, m):
    if MODE:
        await m.reply(text=f"Your current mode is {MODE}")
    elif MODE is None:
        await m.reply(text=f"Set your mode in heroku first")




