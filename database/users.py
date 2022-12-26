from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, DATABASE_NAME

client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
col = db["users"]


async def get_user(user_id):
    user_id = int(user_id)
    user = await col.find_one({"user_id": user_id})
    if not user:
        res = {
            "user_id": user_id,
            "method": "shortener",
            "shortener_api": None,
            "mdisk_api": None,
            "header_text": "",
            "footer_text": "",
            "username": None,
            "base_site": "droplink.co",
            "banner_image": None,
            "is_banner_image": True,
            "is_username": True,
            "is_header_text": True,
            "is_footer_text": True,
            "include_domain": [],
            "exclude_domain": [],
            "banned": False,
        }
        await col.insert_one(res)
        user = await col.find_one({"user_id": user_id})

    return user


async def update_user_info(user_id, value: dict, tag="$set"):
    user_id = int(user_id)
    myquery = {"user_id": user_id}
    newvalues = {tag: value}
    await col.update_one(myquery, newvalues)


async def filter_users(dict):
    return col.find(dict)


async def total_users_count():
    return await col.count_documents({})


async def get_all_users():
    return col.find({})


async def delete_user(user_id):
    await col.delete_one({"user_id": int(user_id)})


async def total_users_count():
    return await col.count_documents({})


async def is_user_exist(id):
    user = await col.find_one({"user_id": int(id)})
    return bool(user)
