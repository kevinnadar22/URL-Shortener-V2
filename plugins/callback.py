from database import db
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helpers import temp, Helpers
from config import SOURCE_CODE
from translation import ADMINS_MESSAGE, BACK_REPLY_MARKUP, BATCH_MESSAGE, CHANNELS_LIST_MESSAGE, CUSTOM_ALIAS_MESSAGE, HELP_MESSAGE, HELP_REPLY_MARKUP, ABOUT_TEXT, ABOUT_REPLY_MARKUP, METHOD_MESSAGE, METHOD_REPLY_MARKUP, OTHER_INFO_MESSAGE, START_MESSAGE, START_MESSAGE_REPLY_MARKUP
from utils import broadcast_admins

import logging
logger = logging.getLogger(__name__)


@Client.on_callback_query()
async def on_callback_query(bot:Client, query:CallbackQuery):

    h = Helpers()
    await query.answer("Loading...")

    if query.data == 'delete':
        await query.message.delete()

    elif query.data == 'help_command':
        await query.message.edit(HELP_MESSAGE.format(
            firstname=temp.FIRST_NAME,
            username=temp.BOT_USERNAME,
            repo=SOURCE_CODE,
            owner="@ask_admin001" ), reply_markup=HELP_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'about_command':
        bot = await bot.get_me()
        await query.message.edit(ABOUT_TEXT.format(bot.mention(style='md')), reply_markup=ABOUT_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'start_command':
        await query.message.edit(START_MESSAGE.format(query.message.from_user.mention, await h.user_method), reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data.startswith('change_method'):
        method_name = query.data.split('#')[1]
        user = temp.BOT_USERNAME
        if not await db.get_bot_method(user):
            await db.add_method(user, method_name)
        else:
            await db.update_method(user, method_name)
        REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Back', callback_data=f'method_command')
    ],

])
        logger.info("Updated method to %s", method_name)
        await broadcast_admins(bot, "Method changed successfully to `{method}` for @{username} by {mention}".format(method=method_name.upper(), username=user, mention=query.from_user.mention))
        await query.message.edit("Method changed successfully to `{method}` for @{username}".format(method=method_name, username=user), reply_markup=REPLY_MARKUP)
    elif query.data == 'method_command':
        user = temp.BOT_USERNAME
        method_name = await db.get_bot_method(user)
        await query.message.edit(METHOD_MESSAGE.format(method=method_name), reply_markup=METHOD_REPLY_MARKUP)
    elif query.data == 'cbatch_command':
        await query.message.edit(BATCH_MESSAGE, reply_markup=BACK_REPLY_MARKUP)

    elif query.data == 'alias_conf':
        await query.message.edit(CUSTOM_ALIAS_MESSAGE, reply_markup=BACK_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'admins_list':
        await query.message.edit(ADMINS_MESSAGE.format(
            admin_list=await h.get_admins
        ), reply_markup=BACK_REPLY_MARKUP)

    elif query.data == 'channels_list':
        await query.message.edit(CHANNELS_LIST_MESSAGE.format(
            channels=await h.get_channels
        ), reply_markup=BACK_REPLY_MARKUP)

    elif query.data == 'other_info':
        await query.message.edit(OTHER_INFO_MESSAGE.format(
            included_domain=await h.get_included_domain,
            excluded_domain=await h.get_excluded_domain,
            source_code=SOURCE_CODE,
            username=await h.get_username,
            header_text=await h.header_text,
            footer_text=await h.footer_text,
            method=await h.user_method,
            droplink_api=await h.user_droplink_api,
            mdisk_api=await h.user_mdisk_api,
        ), reply_markup=BACK_REPLY_MARKUP, disable_web_page_preview=True)

    await query.answer()