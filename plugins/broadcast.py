
import asyncio
import datetime
import logging
import random
import string
import time
import traceback

import aiofiles
import aiofiles.os
from config import ADMINS, BROADCAST_AS_COPY
from database import delete_user, get_all_users, total_users_count
from pyrogram import Client, filters
from pyrogram.errors import (FloodWait, InputUserDeactivated, PeerIdInvalid,
                             UserIsBlocked)
from pyrogram.types import Message

broadcast_ids = {}

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMINS))
async def broadcast_handler(c:Client, m:Message):
    if m.reply_to_message:
        try:
            await main_broadcast_handler(m)
        except Exception as e:
            logging.error("Failed to broadcast", exc_info=True)
    else:
        await m.reply_text("Reply to the message you want to broadcast")

async def send_msg(user_id, message):
    try:
        if BROADCAST_AS_COPY == "False":
            await message.forward(chat_id=user_id)
        elif BROADCAST_AS_COPY == "True":
            await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


async def main_broadcast_handler(m: Message):
    all_users = await get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(text="Broadcast Started! You will be notified with log file when all the users are notified.")

    start_time = time.time()
    total_users = await total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)

    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user['user_id']), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await delete_user(user['user_id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)

    else:
        await m.reply_document(document='broadcast.txt', caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)

    await aiofiles.os.remove('broadcast.txt')
