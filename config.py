import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MODE = os.environ.get("MODE")
DROPLINK_KEY = os.environ.get("DROPLINK_KEY")
MDISK_KEY = os.environ.get("MDISK_KEY")
INCLUDE_DOMAIN = os.environ.get("INCLUDE_DOMAIN")
EXCLUDE_DOMAIN = os.environ.get("EXCLUDE_DOMAIN")
CHANNEL_ID = list(int(i) for i in os.environ.get("CHANNEL_ID").split(" ")) if os.environ.get("CHANNEL_ID") else []
FORWARD_MESSAGE = bool(os.environ.get("FORWARD_MESSAGE"))
ADMINS = list(int(i) for i in os.environ.get("ADMINS").split(",")) if os.environ.get("ADMINS") else []
SOURCE_CODE = "https://github.com/kevinnadar22/URL-Shortener-V2/"


