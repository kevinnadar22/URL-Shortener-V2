from config import *
from motor.motor_asyncio import AsyncIOMotorClient
import helpers

class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.method = self.db['methods']
        self.stats = self.db['stats']
        self.users = self.db['users']

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']
    
    async def get_bot_stats(self):
        return await self.stats.find_one({"bot": helpers.temp.BOT_USERNAME})

    async def create_stats(self):
        await self.stats.insert_one({
            'bot': helpers.temp.BOT_USERNAME,
            'posts': 0,
            'links': 0,
            'mdisk_links': 0,
            'shortener_links': 0
        })

    async def update_posts(self, posts:int):
        myquery = {"bot": helpers.temp.BOT_USERNAME,}
        newvalues = { "$inc": { "posts": posts } }
        return await self.stats.update_one(myquery, newvalues)

    async def update_links(self, links:int, droplink:int=0, mdisk:int=0):
        myquery = {"bot": helpers.temp.BOT_USERNAME,}
        newvalues = { "$inc": { "links": links ,  'mdisk_links': mdisk, 'shortener_links': droplink} }
        return await self.stats.update_one(myquery, newvalues)


db = Database(DATABASE_URL, DATABASE_NAME)
