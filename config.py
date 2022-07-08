import os

if "DYNOS" in os.environ:
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


else:
    API_ID = 4106161
    API_HASH = "bf05f7a4f0a6ac3bc75afb4c89c44be6"
    BOT_TOKEN = '5287186160:AAHbNHvvTQenrZW7-0oDO-5RfR8K60u3__A'
    METHOD = 'mdlink'
    DROPLINK_API ='1aab74171e9891abd0ba799e3fd568c9598a79e1'
    MDISK_API = 'wrnTC42yTIz7eRTARaxM'
    INCLUDE_DOMAIN = os.environ.get("INCLUDE_DOMAIN")
    EXCLUDE_DOMAIN = os.environ.get("EXCLUDE_DOMAIN")
    CHANNEL_ID = [-1001756552101]
    FORWARD_MESSAGE = os.environ.get("FORWARD_MESSAGE", True)
    ADMINS = [1861030649, ]
    SOURCE_CODE = "https://github.com/kevinnadar22/URL-Shortener-V2"
    CHANNELS = os.environ.get("CHANNELS", True)
    USERNAME = os.environ.get("USERNAME", "T2inkss")
    REMOVE_EMOJI = os.environ.get('REMOVE_EMOJI', True)
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "MdiskConvertor")
    DATABASE_URL = os.environ.get("DATABASE_URL", 'mongodb://localhost:27017')