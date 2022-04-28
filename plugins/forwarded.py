# short and repost forwarded message

from pyrogram import Client, filters
from config import CHANNEL_ID, FORWARD_MESSAGE, CHANNELS
import json
from utils import replace_link, replace_mdisk_link, mdisk_droplink_convertor
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import METHOD
import re

# edit forwarded message


@Client.on_message((filters.inline_keyboard | filters.regex(r'https?://[^\s]+')) & filters.chat(CHANNEL_ID) & (
        filters.channel | filters.group) & filters.incoming & ~filters.private & filters.forwarded)
async def channel_forward_link_handler(bot, message):
    if METHOD == "droplink":
        if FORWARD_MESSAGE and CHANNELS is True:

            # reply markup - button post

            if message.reply_markup:
                await message.delete()
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

            # For text messages

            elif message.text:
                text = message.text
                text = await replace_link(text, x="")
                await message.reply_text(text)
                await message.delete()

            # For media or document messages

            elif message.photo:  # for media messages
                fileid = message.photo.file_id
                text = message.caption
                alias = ""
                link = await replace_link(text, alias)
                if link == text:
                    print("The given link is either excluded domain link or a droplink link")
                else:
                    await message.reply_photo(fileid, caption=link)
                    await message.delete()

            elif message.document:  # for document messages
                fileid = message.document.file_id
                text = message.caption
                alias = ""
                link = await replace_link(text, alias)
                if link == text:
                    print("The given link is either excluded domain link or a droplink link")
                else:
                    await message.reply_document(fileid, caption=link)
                    await message.delete()

    elif METHOD == "mdisk":
        if FORWARD_MESSAGE and CHANNELS is True:
            
                # reply markup - button post

                if message.reply_markup:
                    await message.delete()
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

                    txt = await replace_link(txt, x="")
                    await message.reply(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))

                # For text messages

                elif message.text:
                    text = message.text
                    text = await replace_mdisk_link(text)
                    await message.reply_text(text)
                    await message.delete()

                # For media or document messages

                elif message.photo:  # for media messages
                    fileid = message.photo.file_id
                    text = message.caption
                    link = await replace_mdisk_link(text)
                    if link == text:
                        print("The given link is either excluded domain link or a droplink link")
                    else:
                        await message.reply_photo(fileid, caption=link)
                        await message.delete()

                elif message.document:  # for document messages
                    fileid = message.document.file_id
                    text = message.caption
                    alias = ""
                    link = await replace_mdisk_link(text)
                    if link == text:
                        print("The given link is either excluded domain link or a droplink link")
                    else:
                        await message.reply_document(fileid, caption=link)
                        await message.delete()

    elif METHOD == "mdlink":
        if FORWARD_MESSAGE and CHANNELS is True:

            # reply markup - button post

            if message.reply_markup:
                await message.delete()
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

                txt = await mdisk_droplink_convertor(txt)
                await message.reply(text=txt, reply_markup=InlineKeyboardMarkup(buttsons))

            # For text messages

            elif message.text:
                text = message.text
                text = await mdisk_droplink_convertor(text)
                await message.reply_text(text)
                await message.delete()

            # For media or document messages

            elif message.photo:  # for media messages
                fileid = message.photo.file_id
                text = message.caption
                link = await mdisk_droplink_convertor(text)
                if link == text:
                    print("The given link is either excluded domain link or a droplink link")
                else:
                    await message.reply_photo(fileid, caption=link)
                    await message.delete()

            elif message.document:  # for document messages
                fileid = message.document.file_id
                text = message.caption
                alias = ""
                link = await mdisk_droplink_convertor(text)
                if link == text:
                    print("The given link is either excluded domain link or a droplink link")
                else:
                    await message.reply_document(fileid, caption=link)
                    await message.delete()
