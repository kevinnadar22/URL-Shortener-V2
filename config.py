import os

API_ID = int("18413164")
API_HASH = "ab275d22b30fc931aa3324972a95f675"
BOT_TOKEN = "5221302457:AAELQZr8pCFZMGWHwQ2Lq07tojS2oXfzsac"
MODE = "mdisk"
DROPLINK_KEY = "5123699a9d8d535b0065e0e7908e311551527a68"
MDISK_KEY = "6LZq851sXoPHuwqgiKQq"
INCLUDE_DOMAIN = ""
EXCLUDE_DOMAIN = ""
CHANNELS = bool(os.environ.get("CHANNELS"))
CHANNEL_ID = list(int(i) for i in os.environ.get("CHANNEL_ID").split(" ")) if os.environ.get("CHANNEL_ID") else []
FORWARD_MESSAGE = bool(os.environ.get("FORWARD_MESSAGE"))
ADMINS = list(int(i) for i in os.environ.get("ADMINS").split(",")) if os.environ.get("ADMINS") else []
SOURCE_CODE = ""

