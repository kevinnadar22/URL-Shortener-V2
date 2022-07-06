import json
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from utils import replace_mdisk_link, replace_link, get_shortlink, mdisk_droplink_convertor
from config import METHOD, ADMINS, SOURCE_CODE
import re


# Private Chat

@Client.on_message((filters.inline_keyboard | filters.regex(r'https?://[^\s]+')) & filters.private)
async def private_link_handler(bot, message):
    if message.from_user.id in ADMINS:
        if METHOD == "":
            await message.reply_text("Set your METHOD in Heroku vars")
        else:
            if METHOD == "mdisk":
                # url shortener in private chat
                if message.reply_markup:  # reply markup - button post
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

                    txt = await replace_mdisk_link(txt)
                    await message.reply(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))

                elif message.text:  # for text messages
                    text = message.text
                    link = await replace_mdisk_link(text)
                    await message.reply_text(link)

                elif message.photo:  # for media messages
                    fileid = message.photo.file_id
                    text = message.caption
                    link = await replace_mdisk_link(text)
                    await message.reply_photo(fileid, caption=link)

                elif message.document:  # for document messages
                    fileid = message.document.file_id
                    text = message.caption
                    link = await replace_mdisk_link(text)
                    await message.reply_document(fileid, caption=link)

            elif METHOD == "droplink":
                # url shortener in private chat

                if message.reply_markup:  # reply markup - button post
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


                    if message.text:
                        txt = await replace_link(txt, x="")
                        await message.reply(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))
                    elif message.caption:
                        txt = await replace_link(message.caption, x="")
                        if message.photo:
                            await message.reply_photo(photo=message.photo.file_id, caption=txt,
                                                      reply_markup=InlineKeyboardMarkup(buttsons))
                        elif message.document:
                            await message.reply_document(photo=message.document.file_id, caption=txt,
                                                         reply_markup=InlineKeyboardMarkup(buttsons))

                elif message.text:  # for text messages
                    text = message.text
                    if "|" in text:  # For Custom alias
                        alias = text.split('|')[1].replace(" ", "")
                        links = re.findall(r'https?://[^\s]+', text)[0]
                        link = await get_shortlink(links, alias)

                    else:
                        alias = ""
                        link = await replace_link(text, alias)
                    await message.reply_text(link)

                elif message.photo:  # for media messages
                    fileid = message.photo.file_id
                    text = message.caption
                    alias = ""
                    link = await replace_link(text, alias)
                    if link == text:
                        print("The given link is either excluded domain link or a droplink link")
                    else:
                        await message.reply_photo(fileid, caption=link)

                elif message.document:  # for document messages
                    fileid = message.document.file_id
                    text = message.caption
                    alias = ""
                    link = await replace_link(text, alias)
                    if link == text:
                        print("The given link is either excluded domain link or a droplink link")
                    else:
                        await message.reply_document(fileid, caption=link)

            elif METHOD == "mdlink":
                # url shortener in private chat
                if message.reply_markup:  # reply markup - button post
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

                    if message.text:
                        txt = await mdisk_droplink_convertor(txt)
                        await message.reply(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))
                    elif message.caption:
                        txt = await mdisk_droplink_convertor(message.caption)
                        if message.photo:
                            await message.reply_photo(photo=message.photo.file_id, caption=txt,
                                                      reply_markup=InlineKeyboardMarkup(buttsons))
                        elif message.document:
                            await message.reply_document(photo=message.document.file_id, caption=txt,
                                                         reply_markup=InlineKeyboardMarkup(buttsons))

                elif message.text:  # for text messages
                    text = message.text
                    if "|" in text:  # For Custom alias
                        alias = text.split('|')[1].replace(" ", "")
                        links = re.findall(r'https?://[^\s]+', text)[0]
                        link = await mdisk_droplink_convertor(links)

                    else:
                        alias = ""
                        link = await mdisk_droplink_convertor(text)
                    await message.reply_text(link)

                elif message.photo:  # for media messages
                    fileid = message.photo.file_id
                    text = message.caption
                    alias = ""
                    link = await mdisk_droplink_convertor(text)
                    if link == text:
                        print("The given link is either excluded domain link or a droplink link")
                    else:
                        await message.reply_photo(fileid, caption=link)

                elif message.document:  # for document messages
                    fileid = message.document.file_id
                    text = message.caption
                    alias = ""
                    link = await mdisk_droplink_convertor(text)
                    if link == text:
                        print("The given link is either excluded domain link or a droplink link")
                    else:
                        await message.reply_document(fileid, caption=link)

    elif message.from_user.id not in ADMINS:
        await message.reply_text(f"This bot works only for ADMINS of this bot. Make your own Bot.\n\n"
                                 f"[Source Code]({SOURCE_CODE})")
