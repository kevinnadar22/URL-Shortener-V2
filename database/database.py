# (c) @Royalkrrishna


from config import *
from motor.motor_asyncio import AsyncIOMotorClient
import helpers

class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.method = self.db['methods']
        self.stats = self.db['stats']

    async def get_bot_method(self, bot):
        user_method = await self.method.find_one({"bot": bot})
        if user_method:
            return user_method['method']

    async def add_method(self, bot, method):
        await self.method.insert_one(
            {"bot": bot, "method": method}
        )

    async def update_method(self, bot, method):
        myquery = {"bot": bot}
        newvalues = { "$set": { "method": method } }
        await self.method.update_one(myquery, newvalues)

    async def get_db_size(self):
        size = (await self.db.command("dbstats"))['dataSize']
        return size
    
    async def get_bot_stats(self):
        return await self.stats.find_one({"bot": helpers.temp.BOT_USERNAME})

    async def create_stats(self):
        await self.stats.insert_one({
            'bot': helpers.temp.BOT_USERNAME,
            'posts': 0,
            'links': 0,
            'mdisk_links': 0,
            'droplink_links': 0
        })

    async def update_posts(self, posts:int):
        myquery = {"bot": helpers.temp.BOT_USERNAME,}
        newvalues = { "$inc": { "posts": posts } }
        return await self.stats.update_one(myquery, newvalues)

    async def update_links(self, links:int, droplink:int=0, mdisk:int=0):
        myquery = {"bot": helpers.temp.BOT_USERNAME,}
        newvalues = { "$inc": { "links": links ,  'mdisk_links': mdisk, 'droplink_links': droplink} }
        return await self.stats.update_one(myquery, newvalues)


db = Database(DATABASE_URL, DATABASE_NAME)
