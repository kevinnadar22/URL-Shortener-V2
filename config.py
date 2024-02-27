import os

from dotenv import load_dotenv

load_dotenv()


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# Mandatory variables for the bot to start
# API ID from https://my.telegram.org/auth
API_ID = int(os.environ.get("API_ID", "9277335"))
# API Hash from https://my.telegram.org/auth
API_HASH = os.environ.get("API_HASH", "3fbed5d90d8820172f9f251269c01479")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6137243599:AAGXMQDo2JxHGq_k4BJ8sL_CA8iBSrq_iUE")  # Bot token from @BotFather
ADMINS = (
    [int(i.strip()) for i in os.environ.get("ADMINS").split("1255023013")]
    if os.environ.get("ADMINS")
    else []
)

DATABASE_NAME = os.environ.get("DATABASE_NAME", "RoyalMoney72")
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb+srv://RoyalMoney:khan7860@cluster0.cvmo0sz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
)  # mongodb uri from https://www.mongodb.com/
OWNER_ID = int(os.environ.get("OWNER_ID", "1807927334"))  # id of the owner
ADMINS.append(OWNER_ID) if OWNER_ID not in ADMINS else []

#  Optionnal variables
LOG_CHANNEL = int(
    os.environ.get("LOG_CHANNEL", "-1002024698762")
)  # log channel for information about users
UPDATE_CHANNEL = int(os.environ.get(
    "UPDATE_CHANNEL", "@Royal_Money_online")  # For Force Subscription
BROADCAST_AS_COPY = is_enabled(
    (os.environ.get("BROADCAST_AS_COPY", "False")), False
)  # true if forward should be avoided
IS_PRIVATE = is_enabled(
    os.environ.get("IS_PRIVATE", "False"), "False"
)  # true for private use and restricting users
SOURCE_CODE = os.environ.get(
    "SOURCE_CODE", "https://github.com/kevinnadar22/URL-Shortener-V2"
)  # for upstream repo
# image when someone hit /start
WELCOME_IMAGE = os.environ.get("WELCOME_IMAGE", "https://telegra.ph/file/5e82ce4c35739b851aa40.jpg")
LINK_BYPASS = is_enabled(
    (os.environ.get("LINK_BYPASS", "False")), False
)  # if true, urls will be bypassed
# your shortener site domain
BASE_SITE = os.environ.get("BASE_SITE", "RoyalMoney.online")

# For Admin use
CHANNELS = is_enabled((os.environ.get("CHANNELS", "True")), True)
CHANNEL_ID = (
    [int(i.strip()) for i in os.environ.get("CHANNEL_ID").split("-1002095382800")]
    if os.environ.get("CHANNEL_ID")
    else []
)

DE_BYPASS = (
    [i.strip() for i in os.environ.get("DE_BYPASS").split(",")]
    if os.environ.get("DE_BYPASS")
    else []
)
DE_BYPASS.append("mdisk.me")

FORWARD_MESSAGE = is_enabled(
    (os.environ.get("FORWARD_MESSAGE", "False")), False
)  # true if forwardd message to converted by reposting the post


WEB_SERVER = is_enabled(os.environ.get("WEB_SERVER", "True"), True)
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "240"))
PORT = int(os.environ.get("PORT", "8000"))
