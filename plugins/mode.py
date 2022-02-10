from pyrogram import Client, filters
from config import METHOD


@Client.on_message(filters.command('mode') & filters.private)
async def mode_message(c, m):
    if METHOD:
        await m.reply(text=f"Your current mode is {METHOD}")
    elif METHOD is None:
        await m.reply(text=f"Set your mode in heroku first")




