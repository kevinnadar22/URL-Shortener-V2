import asyncio
from database import db
from translation import BATCH
from helpers import AsyncIter, temp
from pyrogram import Client, filters
from utils import main_convertor_handler
from config import CHANNELS, ADMINS, SOURCE_CODE
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid

lock = asyncio.Lock()


cancel_button = [[
    InlineKeyboardButton('Cancel 🔐', callback_data='cancel_process')
]
]


@Client.on_message(filters.private & filters.command('batch'))
async def batch(c, m):
    user_method = await db.get_bot_method(temp.BOT_USERNAME)
    if m.from_user.id in ADMINS:
        if not user_method:
            return await m.reply("Set your /method first")
        else:
            if CHANNELS is True or CHANNELS == "True":
                if len(m.command) < 2:
                    await m.reply_text(BATCH)
                else:
                    channel_id = m.command[1]
                    if channel_id.startswith("@"):
                        channel_id = channel_id.split("@")[1]
                    elif channel_id.startswith("-100"):
                        channel_id = int(channel_id)

                    buttons = [
[
    InlineKeyboardButton('Batch Short 🏕', callback_data=f'batch#{str(channel_id)}')
],
[
    InlineKeyboardButton('Cancel 🔐', callback_data='cancel')
]
]

                    await m.reply(text=f"Are you sure you want to batch short?\n\nChannel: {channel_id}", reply_markup=InlineKeyboardMarkup(buttons))

            elif CHANNELS is False or CHANNELS == "False":
                await m.reply(text="Set your CHANNELS var to True in HEROKU to use this command")
    elif m.from_user.id not in ADMINS:
        await m.reply_text(f"""This bot works only for ADMINS of this bot. Make your own Bot.\n\n[Source Code]({SOURCE_CODE})""")


@Client.on_callback_query(filters.regex(r'^cancel') | filters.regex(r'^batch'))
async def cancel(c:Client, m:CallbackQuery):

    user_method = await db.get_bot_method(temp.BOT_USERNAME)

    if m.data == "cancel":
        await m.message.delete()
        return
    elif m.data.startswith('batch'): 

        if lock.locked():
            return await m.answer('Wait until previous process complete.', show_alert=True)
            
        channel_id = int(m.data.split('#')[1])
        try:
            txt = await c.send_message(channel_id, ".")
            id = txt.id
            await txt.delete()
        except ChatWriteForbidden:
            return await m.message.edit("Bot is not an admin in the given channel")
        except PeerIdInvalid:
            return await m.message.edit("Given channel ID is invalid")

        txt = await m.message.edit(text=f"Batch Shortening Started!\n\n Channel: {channel_id}\n\nTo Cancel /cancel",)

        success = 0
        fail = 0
        total = 0
        empty=0

        channel_posts = AsyncIter(await c.get_messages(channel_id, (range(id, 1, -1))))

        temp.CANCEL = False

        async with lock:

            try:

                async for message in channel_posts:

                    if temp.CANCEL == True:
                        break

                    if message.media or message.text:
                        try:
                            await main_convertor_handler(message=message, type=user_method, edit_caption=True)
                            success += 1
                        except:
                            print(e)
                            fail+=1
                        await asyncio.sleep(1)
                    else:
                        empty += 1
                    total+=1

                    if total % 10 == 0:
                        msg = f"Batch Shortening in Process !\n\nTotal: {total}\nSuccess: {success}\nFailed: {fail}\nEmpty: {empty}\n\nTo cancel the batch: /cancel"
                        await txt.edit((msg))
                        continue

            except Exception as e:
                print(e)
            else:
                await asyncio.sleep(10)
                msg = f"Batch Shortening Completed!\n\nTotal: `{total}`\nSuccess: `{success}`\nFailed: `{fail}`\nEmpty: `{empty}`"
                await txt.edit(msg)
        


@Client.on_message(filters.command('cancel'))
async def stop_button(c, m):
    if m.from_user.id in ADMINS:
        temp.CANCEL = True
        msg = await c.send_message(
            text="<i>Trying To Stoping.....</i>",
            chat_id=m.chat.id
        )
        await asyncio.sleep(5)
        await msg.edit("Batch Shortening Stopped Successfully 👍")
