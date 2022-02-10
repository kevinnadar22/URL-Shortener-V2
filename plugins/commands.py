from pyrogram import Client, filters
from translation import START_MESSAGE, HELP_MESSAGE, ABOUT_TEXT
from config import METHOD


@Client.on_message(filters.command('start'))
async def start(c, m):
    if METHOD == "":
        mode = "None"
    else:
        mode = METHOD
    await m.reply_text(START_MESSAGE.format(m.from_user.mention, mode))


@Client.on_message(filters.command('help'))
async def help_command(c, m):
    await m.reply_text(HELP_MESSAGE, disable_web_page_preview=True)


@Client.on_message(filters.command('about'))
async def about_command(c, m):
    bot = await c.get_me()
    await m.reply_text(ABOUT_TEXT.format(bot.mention(style='md')), disable_web_page_preview=True)
