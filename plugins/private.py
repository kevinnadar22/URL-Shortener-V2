import json
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from utils import replace_mdisk_link, replace_link, get_shortlink
from config import MODE, ADMINS, SOURCE_CODE
import re


# Private Chat

@Client.on_message((filters.inline_keyboard | filters.regex(r'https?://[^\s]+')) & filters.private & ~filters.edited)
async def private_link_handler(bot, message):
    if message.from_user.id in ADMINS:
        if MODE == "":
            await message.reply_text("Set your MODE in Heroku vars")
        else:
            if MODE == "mdisk":
                links = re.findall(r'https?://mdisk.me[^\s]+', message.text)
                if len(links) == 0:
                    await message.reply_text("Send any MDISK link to save it to your mdisk account")
                # url shortener in private chat
                else:
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

            elif MODE == "droplink":
                # url shortener in private chat
                print(True)

                if message.reply_markup:  # reply markup - button post
                    txt = message.text
                    print(message)
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
                    print(txt)

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

    elif message.from_user.id not in ADMINS:
        await message.reply_text(f"This bot works only for ADMINS of this bot. Make your own Bot.\n\n"
                                 f"[Source Code]({SOURCE_CODE})")
