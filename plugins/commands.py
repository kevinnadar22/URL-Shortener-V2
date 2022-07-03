from webbrowser import get
from pyrogram import Client, filters
from translation import *
from config import ADMINS
from pyrogram.types import Message
from database import db

@Client.on_message(filters.command('start'))
async def start(c, m):
    bot = await c.get_me()
    user_method = await db.get_bot_method(bot.username)
    if not user_method:
        mode = "None"
    else:
        mode = user_method
    await m.reply_text(START_MESSAGE.format(m.from_user.mention, mode))


@Client.on_message(filters.command('help'))
async def help_command(c, m):
    await m.reply_text(HELP_MESSAGE, disable_web_page_preview=True)


@Client.on_message(filters.command('about'))
async def about_command(c, m):
    bot = await c.get_me()
    await m.reply_text(ABOUT_TEXT.format(bot.mention(style='md')), disable_web_page_preview=True)


@Client.on_message(filters.command('method') & filters.chat(ADMINS) & filters.private)
async def method_handler(c:Client, m:Message):
    user = await c.get_me()
    print(user.username)
    user_method = await db.get_bot_method(user.username)
    if len(m.command) == 1:    
        return await m.reply_text(METHOD_MESSAGE.format(method=user_method))
    if len(m.command) == 2:
        method_name = m.command[1]

        if method_name not in ['mdisk', 'mdlink', 'droplink']:
            return await m.reply_text(METHOD_MESSAGE.format(method=user_method))

        if not await db.get_bot_method(user.username):
            await db.add_method(user.username, method_name)
        else:
            await db.update_method(user.username, method_name)
        await m.reply("Method changed successfully to {method} for @{username}".format(method=method_name, username=user.username))