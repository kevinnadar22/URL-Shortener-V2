# (c) @Royalkrrishna

from config import *
import pymongo


class Database:
    def __init__(self, uri, database_name):
        self._client = pymongo.MongoClient(uri)
        self.db = self._client[database_name]
        self.method = self.db['methods']

    async def get_bot_method(self, bot):
        user_method = self.method.find_one({"bot": bot})
        if user_method:
            return user_method['method']

    async def add_method(self, bot, method):
        self.method.insert_one(
            {"bot": bot, "method": method}
        )

    async def update_method(self, bot, method):
        myquery = {"bot": bot}
        newvalues = { "$set": { "method": method } }
        self.method.update_one(myquery, newvalues)


db = Database(DATABASE_URL, DATABASE_NAME)
