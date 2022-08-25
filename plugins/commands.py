import datetime
import json
import logging

from validators import domain
from config import (ADMINS, HEROKU, HEROKU_API_KEY, HEROKU_APP_NAME,
                    IS_PRIVATE, LOG_CHANNEL, SOURCE_CODE, WELCOME_IMAGE)
from database import db
from database.users import (filter_users, get_user, is_user_exist,
                            total_users_count, update_user_info)
from helpers import temp
from pyrogram import Client, filters
from pyrogram.types import Message
from translation import *
from utils import extract_link, get_me_button, get_size, getHerokuDetails

logger = logging.getLogger(__name__)

user_commands = ["mdisk_api", "shortener_api", "header", "footer", "username", "banner_image", "base_site", "me"]
avl_web = ["droplink.co", "gplinks.in", "tnlink.in", "za.gl", "du-link.in", "viplink.in", "shorturllink.in", "shareus.in", "earnspace.in",]

avl_web1 = ""

for i in avl_web:
    avl_web1+= f"- {i}\n"

@Client.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c:Client, m:Message):
    
    NEW_USER_REPLY_MARKUP = [
                [
                    InlineKeyboardButton('Ban', callback_data=f'ban#{m.from_user.id}'),
                    InlineKeyboardButton('Close', callback_data='delete'),
                ]
            ]
    is_user = await is_user_exist(m.from_user.id)

    reply_markup = InlineKeyboardMarkup(NEW_USER_REPLY_MARKUP)

    if not is_user and LOG_CHANNEL: await c.send_message(LOG_CHANNEL, f"#NewUser\n\nUser ID: `{m.from_user.id}`\nName: {m.from_user.mention}", reply_markup=reply_markup)
    new_user = await get_user(m.from_user.id)  
    t = START_MESSAGE.format(m.from_user.mention, new_user["method"], new_user["base_site"])

    if WELCOME_IMAGE:
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=t, reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)
    await m.reply_text(t, reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)


@Client.on_message(filters.command('help') & filters.private)
async def help_command(c, m: Message):
    s = HELP_MESSAGE.format(
                firstname=temp.FIRST_NAME,
                username=temp.BOT_USERNAME,
                repo=SOURCE_CODE,
                owner="@ask_admin001" )

    if WELCOME_IMAGE:
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=s, reply_markup=HELP_REPLY_MARKUP)
    await m.reply_text(s, reply_markup=HELP_REPLY_MARKUP, disable_web_page_preview=True)


@Client.on_message(filters.command('about'))
async def about_command(c, m: Message):
    reply_markup=ABOUT_REPLY_MARKUP

    bot = await c.get_me()
    if WELCOME_IMAGE:
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=ABOUT_TEXT.format(bot.mention(style='md')), reply_markup=reply_markup, disable_web_page_preview=True)
    await m.reply_text(ABOUT_TEXT.format(bot.mention(style='md')),reply_markup=reply_markup , disable_web_page_preview=True)


@Client.on_message(filters.command('method') &  filters.private)
async def method_handler(c:Client, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = METHOD_MESSAGE.format(method=user["method"], shortener=user["base_site"],)
        return await m.reply(s, reply_markup=METHOD_REPLY_MARKUP)
    elif len(cmd) == 2:    
        method = cmd[1]
        if method in ["mdisk", "mdlink", "shortener"]:
            await update_user_info(user_id, {"method": method })
            await m.reply("Method updated successfully to " + method)
        else:
            return await m.reply(METHOD_MESSAGE.format(method=user["method"]))

@Client.on_message(filters.command('restart') & filters.user(ADMINS) & filters.private)
async def restart_handler(c: Client, m:Message):
    RESTARTE_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Sure', callback_data=f'restart'),
        InlineKeyboardButton('Disable', callback_data=f'delete'),

    ],

])

    await m.reply("Are you sure you want to restart / re-deploy the server?", reply_markup=RESTARTE_MARKUP)


@Client.on_message(filters.command('stats') & filters.private)
async def stats_handler(c: Client, m:Message):
    try:
        txt = await m.reply('`Fetching stats...`')
        size = await db.get_db_size()
        free = 536870912 - size
        size = await get_size(size)
        free = await get_size(free)
        link_stats = await db.get_bot_stats()
        runtime = datetime.datetime.now()

        t = runtime - temp.START_TIME
        runtime = str(datetime.timedelta(seconds=t.seconds))
        total_users = await total_users_count()

        msg = f"""
**- Total Users:** `{total_users}`
**- Total Posts Sent:** `{link_stats['posts']}`
**- Total Links Shortened:** `{link_stats['links']}`
**- Total Mdisk Links Shortened:** `{link_stats['mdisk_links']}`
**- Total Shortener Links Shortened:** `{link_stats['shortener_links']}`
**- Used Storage:** `{size}`
**- Total Free Storage:** `{free}`

**- Runtime:** `{runtime}`
    """
        if HEROKU and m.from_user.id in ADMINS:
            heroku = await getHerokuDetails(HEROKU_API_KEY, HEROKU_APP_NAME)
            msg += f"\n- **Heroku Stats:**\n{heroku}"

        return await txt.edit(msg)
    except Exception as e:
        logging.error(e, exc_info=True)


@Client.on_message(filters.command('logs') & filters.user(ADMINS) & filters.private)
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('mdisk_api') & filters.private)
async def mdisk_api_handler(bot, message:Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    cmd = message.command

    if len(cmd) == 1:
        return await message.reply(MDISK_API_MESSAGE.format(user["mdisk_api"]))

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"mdisk_api": api})
        await message.reply("Mdisk API updated successfully to " + api)


@Client.on_message(filters.command('shortener_api') & filters.private)
async def shortener_api_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"])

        return await m.reply(s)
    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("Shortener API updated successfully to " + api)

@Client.on_message(filters.command('header') & filters.private)
async def header_handler(bot, m:Message):
    user_id = m.from_user.id
    cmd = m.command
    user = await get_user(user_id)

    if m.reply_to_message:    
        header_text = m.reply_to_message.text.html
        await update_user_info(user_id, {"header_text": header_text})
        await m.reply("Header Text Updated Successfully")
    else:
        if "remove" in cmd:
            await update_user_info(user_id, {"header_text": ""})
            return await m.reply("Header Text Successfully Removed")
        else:
            return await m.reply(HEADER_MESSAGE + "\n\nCurrent Header Text: " + user["header_text"].replace(r"\n", "\n"))

@Client.on_message(filters.command('footer') & filters.private)
async def footer_handler(bot, m:Message):
    user_id = m.from_user.id
    cmd = m.command
    user = await get_user(user_id)

    if not m.reply_to_message:
        if "remove" in cmd:
            await update_user_info(user_id, {"footer_text": ""})
            return await m.reply("Footer Text Successfully Removed")
        else:
            return await m.reply(FOOTER_MESSAGE + "\n\nCurrent Footer Text: " + user["footer_text"].replace(r"\n", "\n"))
    elif m.reply_to_message.text:    
        footer_text = m.reply_to_message.text.html
        await update_user_info(user_id, {"footer_text": footer_text})
        await m.reply("Footer Text Updated Successfully")

@Client.on_message(filters.command('username') & filters.private)
async def username_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        username = user["username"] if user["username"] else None
        return await m.reply(USERNAME_TEXT.format(username=username))
    elif len(cmd) == 2:    
        if "remove" in cmd:
            await update_user_info(user_id, {"username": ""})
            return await m.reply("Username Successfully Removed")
        else:
            username = cmd[1].strip().replace("@", "")
            await update_user_info(user_id, {"username": username})
            await m.reply("Username updated successfully to " + username)


@Client.on_message(filters.command('banner_image') & filters.private)
async def banner_image_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        if m.reply_to_message and m.reply_to_message.photo:
            # Getting the file_id of the photo that was sent to the bot.
            fileid = m.reply_to_message.photo.file_id
            await update_user_info(user_id, {"banner_image": fileid})
            return await m.reply_photo(fileid, caption="Banner Image updated successfully")
        else:
            if user["banner_image"]:
                return await m.reply_photo(user["banner_image"], caption=BANNER_IMAGE)
            else:
                return await m.reply("Current Banner Image URL: None\n" + BANNER_IMAGE)
    elif len(cmd) == 2:    
        if "remove" in cmd:
            await update_user_info(user_id, {"banner_image": ""})
            return await m.reply("Banner Image Successfully Removed")
        else:
            image_url = cmd[1].strip()
            valid_image_url = await extract_link(image_url)
            if valid_image_url:
                await update_user_info(user_id, {"banner_image": image_url})
                return await m.reply_photo(image_url, caption="Banner Image updated successfully")
            else:
                return await m.reply_text("Image URL is Invalid")

@Client.on_message(filters.command('base_site') & filters.private)
async def base_site_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    site = user['base_site']
    text = f"`/base_site (base_site)`\n\nCurrent base site: {site}\n\n EX: `/base_site shareus.in`\n\nAvailable base sites:\n{avl_web1}\nAnd All alternate sites to droplink.co"
    if len(cmd) == 1:
        return await m.reply(
        text=text,
        disable_web_page_preview=True)
    elif len(cmd) == 2:    
        base_site = cmd[1].strip()
        if not domain(base_site):
            return await m.reply(text=text,disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("Base Site updated successfully")


@Client.on_message(filters.command('me') & filters.private)
async def me_handler(bot, m:Message):
    user_id = m.from_user.id
    user = await get_user(user_id)

    user_id = m.from_user.id
    user = await get_user(user_id)
    res = USER_ABOUT_MESSAGE.format(
                base_site=user["base_site"], 
                method=user["method"], 
                shortener_api=user["shortener_api"], 
                mdisk_api=user["mdisk_api"],
                username=user["username"],
                header_text=user["header_text"].replace(r'\n', '\n') if user["header_text"] else None,
                footer_text=user["footer_text"].replace(r'\n', '\n') if user["footer_text"] else None,
                banner_image=user["banner_image"])

    buttons = await get_me_button(user)
    reply_markup = InlineKeyboardMarkup(buttons)
    return await m.reply_text(res, reply_markup=reply_markup, disable_web_page_preview=True)


#  Todo
@Client.on_message(filters.command('include_domain') & filters.private)
async def include_domain_handler(bot, m:Message):
    user = await get_user(m.from_user.id)
    inc_domain = user["include_domain"]
    tdl = ""
    if inc_domain:
        for i in inc_domain:
            tdl+= f"- `{i}`\n"
    else:
        tdl = "None\n"

    if len(m.command) == 1:
        return await m.reply(INCLUDE_DOMAIN_TEXT.format(tdl))
    else:
        try:
            cmd = m.command
            cmd.remove('include_domain')

            if "remove_all" in cmd:
                domain_list = []

            elif "remove" in cmd:

                cmd.remove('remove')
                domain_list_cmd = ("".join(cmd)).strip().split(",") 

                for i in list(domain_list_cmd):
                    try:
                        inc_domain.remove(i)
                    except:
                        pass
                
                domain_list = list(set(list(inc_domain)))

            else:
                domain_list_cmd = ("".join(cmd)).strip().split(",") 
                domain_list = list(set(domain_list_cmd+list(inc_domain)))

            x = await update_user_info(m.from_user.id, {"include_domain":domain_list}, )
            return await m.reply("Updated include domain list successfully") 
        except Exception as e:
            logging.exception(e, exc_info=True)
            return await m.reply("Some error updating include domain list")


@Client.on_message(filters.command('exclude_domain') & filters.private)
async def exclude_domain_handler(bot, m:Message):
    user = await get_user(m.from_user.id)
    ex_domain = user["exclude_domain"]
    tdl = ""
    if ex_domain:
        for i in ex_domain:
            tdl+= f"- `{i}`\n"
    else:
        tdl = "None\n"

    if len(m.command) == 1:
        return await m.reply(EXCLUDE_DOMAIN_TEXT.format(tdl))
    else:
        try:
            cmd = m.command
            cmd.remove('exclude_domain')

            if "remove_all" in cmd:
                domain_list = []

            elif "remove" in cmd:

                cmd.remove('remove')
                domain_list_cmd = ("".join(cmd)).strip().split(",") 

                for i in list(domain_list_cmd):
                    try:
                        ex_domain.remove(i)
                    except:
                        pass
                
                domain_list = list(set(list(ex_domain)))

            else:
                domain_list_cmd = ("".join(cmd)).strip().split(",") 
                domain_list = list(set(domain_list_cmd+list(ex_domain)))

            x = await update_user_info(m.from_user.id, {"exclude_domain":domain_list}, )
            return await m.reply("Updated exclude domain list successfully") 
        except Exception as e:
            logging.exception(e, exc_info=True)
            return await m.reply("Some error updating exclude domain list")


@Client.on_message(filters.command('ban') & filters.private & filters.user(ADMINS))
async def banned_user_handler(c:Client, m:Message):
    try:
        if len(m.command) == 1:
                banned_users = await filter_users({"banned": True})
                x = ""
                async for user in banned_users:
                    x += f"- `{user['user_id']}`\n"

                txt = BANNED_USER_TXT.format(users=x if x else "None")
                await m.reply(txt)

        elif len(m.command) == 2:
            user_id = m.command[1]
            user = await get_user(int(user_id))

            if user:
                if not user["banned"]:
                    await update_user_info(user_id, {"banned": True})
                    try:
                        await c.send_message(user_id, "You are now banned from the bot by Admin")
                    except Exception as e:
                        pass
                    await m.reply(f"User [`{user_id}`] has been banned from the bot. To Unban. `/unban {user_id}`")
                else:
                    await m.reply("User is already banned")

            else:
                await m.reply("User doesn't exist")
    except Exception as e:
        logging.exception(e, exc_info=True)

@Client.on_message(filters.command('unban') & filters.private & filters.user(ADMINS))
async def unban_user_handler(c:Client, m:Message):
    try:
        if len(m.command) == 1:
                banned_users = await filter_users({"banned": True})
                x = ""
                async for user in banned_users:
                    x += f"- `{user['user_id']}`\n"

                txt = BANNED_USER_TXT.format(users=x if x else "None")
                await m.reply(txt)

        elif len(m.command) == 2:
            user_id = m.command[1]
            user = await get_user(int(user_id))

            if user:
                if user["banned"]:
                    await update_user_info(user_id, {"banned": False})
                    try:
                        await c.send_message(user_id, "You are now free to use the bot. You have been unbanned by the Admin")
                    except Exception as e:
                        pass
                    await m.reply(f"User [`{user_id}`] has been unbanned from the bot. To ban. `/ban {user_id}`")
                else:
                    await m.reply("User is not banned yet")

            else:
                await m.reply("User doesn't exist")
    except Exception as e:
        logging.exception(e, exc_info=True)


@Client.on_message(filters.command('info') & filters.private & filters.user(ADMINS))
async def get_user_info_handler(c:Client, m:Message):
    try:
        if len(m.command) == 2:
            user = await get_user(int(m.command[1]))
            if user:
                res = USER_ABOUT_MESSAGE.format(
                            base_site=user["base_site"], 
                            method=user["method"], 
                            shortener_api='This is something secret', 
                            mdisk_api='This is something secret',
                            username=user["username"],
                            header_text=user["header_text"].replace(r'\n', '\n') if user["header_text"] else None,
                            footer_text=user["footer_text"].replace(r'\n', '\n') if user["footer_text"] else None,
                            banner_image=user["banner_image"])
                
                res = f'User: `{user["user_id"]}`\n{res}'

                reply_markup = InlineKeyboardMarkup([
                        [
                        InlineKeyboardButton('Ban', callback_data=f'ban#{user["user_id"]}'),
                        InlineKeyboardButton('Close', callback_data='delete')
                    ],

                ])
                return await m.reply_text(res, reply_markup=reply_markup, quote=True)
            else:
                return await m.reply_text("User doesn't exist")

        else:
            return await m.reply_text("`/info user_id`")
    except Exception as e:
        await m.reply_text(e)
        logging.error(e)