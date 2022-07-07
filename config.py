import os


API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DROPLINK_API = os.environ.get("DROPLINK_API")
MDISK_API = os.environ.get("MDISK_API")
INCLUDE_DOMAIN = os.environ.get("INCLUDE_DOMAIN")
EXCLUDE_DOMAIN = os.environ.get("EXCLUDE_DOMAIN")
CHANNEL_ID = list(int(i.strip()) for i in os.environ.get("CHANNEL_ID").split(" ")) if os.environ.get("CHANNEL_ID") else []
FORWARD_MESSAGE = (os.environ.get("FORWARD_MESSAGE"))
ADMINS = list(int(i.strip()) for i in os.environ.get("ADMINS").split(",")) if os.environ.get("ADMINS") else []
SOURCE_CODE = "https://github.com/kevinnadar22/URL-Shortener-V2"
CHANNELS = bool(os.environ.get("CHANNELS"))
USERNAME = os.environ.get("USERNAME", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "MdiskConvertor")
DATABASE_URL = os.environ.get("DATABASE_URL",)
REMOVE_EMOJI = os.environ.get("REMOVE_EMOJI", False)

