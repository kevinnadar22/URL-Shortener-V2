import asyncio
import json
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNELS, ADMINS, SOURCE_CODE
from utils import replace_link, replace_mdisk_link, mdisk_droplink_convertor
from config import METHOD
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
import os
import sys
from pyrogram import Client, filters
from translation import BATCH

buttons = [
    [
        InlineKeyboardButton('Batch Short 🏕', callback_data='batch')
    ],
    [
        InlineKeyboardButton('Cancel 🔐', callback_data='cancel')
    ]
]

cancel_button = [[
    InlineKeyboardButton('Cancel 🔐', callback_data='cancel_process')
]
]

channel_id = ""


@Client.on_message(filters.private & filters.command('batch'))
async def batch(c, m):
    if m.from_user.id in ADMINS:
        if METHOD == "":
            await m.reply_text("Set your METHOD in Heroku vars")
        else:
            global channel_id

            if CHANNELS is True:
                if len(m.command) < 2:
                    await m.reply_text(BATCH)
                else:
                    channel_id = m.command[1]
                    if channel_id.startswith("@"):
                        channel_id = channel_id.split("@")[1]
                    elif channel_id.startswith("-100"):
                        channel_id = int(channel_id)
                    elif channel_id.startswith("t.me"):
                        channel_id = channel_id.split("/")[-1]
                        if channel_id.startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")):
                            channel_id = int(channel_id)
                        else:
                            channel_id = str(channel_id)
                    elif channel_id.startswith("https"):
                        channel_id = channel_id.split("/")[-1]

                    await m.reply(text=f"Are you sure you want to batch short?\n\nChannel: {channel_id}",
                                  reply_markup=InlineKeyboardMarkup(buttons))

            elif CHANNELS is False:
                await m.reply(text="Set your CHANNELS var to True in HEROKU to use this command")
    elif m.from_user.id not in ADMINS:
        await m.reply_text(f"""This bot works only for ADMINS of this bot. Make your own Bot.\n\n[Source Code]({SOURCE_CODE})""")


@Client.on_callback_query(filters.regex(r'^cancel') | filters.regex(r'^batch'))
async def cancel(c, m):
    global channel_id
    if m.data == "cancel":
        await m.message.delete()
    elif m.data == "batch":
        if CHANNELS is True:
            try:
                txt = await c.send_message(channel_id, ".")

                await txt.delete()

            except ChatWriteForbidden:
                await m.message.edit("Bot is not an admin in the given channel")
            await m.message.edit(text=f"Batch Shortening Started!\n\n Channel: {channel_id}\n\nTo Cancel /cancel",

                                 )

            for i in range(txt.id, 1, -1):

                try:
                    message = await c.get_messages(channel_id, i)
                    if METHOD == "droplink":

                        # reply markup - button post

                        if message.reply_markup:
                            txt = message.text
                            reply_markup = json.loads(str(message.reply_markup))
                            buttsons = []
                            for i, markup in enumerate(reply_markup["inline_keyboard"]):
                                buttons = []
                                for j in markup:
                                    text = j["text"]
                                    url = j["url"]
                                    url = await replace_link(url, x="")
                                    button = InlineKeyboardButton(text, url=url)
                                    buttons.append(button)
                                buttsons.append(buttons)

                            txt = await replace_link(txt, x="")
                            await message.edit(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))

                        # For text messages

                        elif message.text:
                            text = message.text
                            text = await replace_link(text, x="")
                            await message.edit(text)

                        # For media or document messages

                        elif message.media or message.document:
                            text = message.caption
                            link = await replace_link(text, x="")
                            if link == text:
                                print("The given link is either excluded domain link or a droplink link")
                            else:
                                await message.edit_caption(link)

                    elif METHOD == "mdisk":

                        # reply markup - button post

                        if message.reply_markup:
                            txt = message.text
                            reply_markup = json.loads(str(message.reply_markup))
                            buttsons = []
                            for i, markup in enumerate(reply_markup["inline_keyboard"]):
                                buttons = []
                                for j in markup:
                                    text = j["text"]
                                    url = j["url"]
                                    url = await replace_mdisk_link(url)
                                    button = InlineKeyboardButton(text, url=url)
                                    buttons.append(button)
                                buttsons.append(buttons)
                    
                            try:
                                if message.text:
                                    txt = await replace_link(txt, x="")
                                    await message.edit(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))
                                elif message.caption:
                                    txt = await replace_link(message.caption, x="")
                                    if message.photo:
                                        await message.edit_caption(photo=message.photo.file_id, caption=txt,
                                                                  reply_markup=InlineKeyboardMarkup(buttsons))
                                    elif message.document:
                                        await message.edit_caption(photo=message.document.file_id, caption=txt,
                                                                     reply_markup=InlineKeyboardMarkup(buttsons))
                            except Exception as e:
                                print(e)

                        # For text messages

                        elif message.text:
                            text = message.text
                            text = await replace_mdisk_link(text)
                            await message.edit(text)

                        # For media or document messages

                        elif message.media or message.document:
                            text = message.caption
                            link = await replace_mdisk_link(text)
                            if link == text:
                                print("The given link is either excluded domain link or a droplink link")
                            else:
                                await message.edit_caption(link)

                    elif METHOD == "mdlink":

                        # reply markup - button post

                        if message.reply_markup:
                            txt = message.text
                            reply_markup = json.loads(str(message.reply_markup))
                            buttsons = []
                            for i, markup in enumerate(reply_markup["inline_keyboard"]):
                                buttons = []
                                for j in markup:
                                    text = j["text"]
                                    url = j["url"]
                                    url = await mdisk_droplink_convertor(url)
                                    button = InlineKeyboardButton(text, url=url)
                                    buttons.append(button)
                                buttsons.append(buttons)

                            try:
                                if message.text:
                                    txt = await mdisk_droplink_convertor(txt)
                                    await message.edit(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))
                                elif message.caption:
                                    txt = await mdisk_droplink_convertor(message.caption)
                                    if message.photo:
                                        await message.edit_caption(photo=message.photo.file_id, caption=txt,
                                                                   reply_markup=InlineKeyboardMarkup(buttsons))
                                    elif message.document:
                                        await message.edit_caption(photo=message.document.file_id, caption=txt,
                                                                   reply_markup=InlineKeyboardMarkup(buttsons))
                            except Exception as e:
                                print(e)

                        # For text messages

                        elif message.text:
                            text = message.text
                            text = await mdisk_droplink_convertor(text)
                            await message.edit(text)

                        # For media or document messages

                        elif message.media or message.document:
                            text = message.caption
                            link = await mdisk_droplink_convertor(text)
                            if link == text:
                                print("The given link is either excluded domain link or a droplink link")
                            else:
                                await message.edit_caption(link)

                    await asyncio.sleep(1)
                except:
                    pass


@Client.on_message(filters.command('cancel'))
async def stop_button(c, m):
    if m.from_user.id in ADMINS:
        print("Cancelled")
        msg = await c.send_message(
            text="<i>Trying To Stoping.....</i>",
            chat_id=m.chat.id
        )
        await asyncio.sleep(5)
        await msg.edit("Batch Shortening Stopped Successfully 👍")
        os.execl(sys.executable, sys.executable, *sys.argv)
