# temp db for banned 

import database
from config import ADMINS, CHANNEL_ID, CHANNELS, EXCLUDE_DOMAIN, FOOTER_TEXT, HEADER_TEXT, MDISK_API, DROPLINK_API, INCLUDE_DOMAIN, USERNAME


class temp(object): # Eva Maria Idea of Temping
    BOT_USERNAME = None
    CANCEL = False
    FIRST_NAME = None
    START_TIME = None
    
class AsyncIter:    
    def __init__(self, items):    
        self.items = items    

    async def __aiter__(self):    
        for item in self.items:    
            yield item  

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration



class Helpers:
    def __init__(self):
        self.username = temp.BOT_USERNAME

    @property
    async def user_mdisk_api(self):
        return MDISK_API

    @property
    async def user_droplink_api(self):
        return DROPLINK_API
    
    @property
    async def user_method(self):
        user_method = await database.db.get_bot_method(self.username)
        if user_method:
            return user_method
        return "None"

    @property
    async def get_included_domain(self):
        x=''
        if INCLUDE_DOMAIN:   
            async for i in AsyncIter(INCLUDE_DOMAIN):
                x+= f"- `{i}`"
            return x
        return "No Included Domain"

    @property
    async def get_excluded_domain(self):
        x=''
        if EXCLUDE_DOMAIN:   
            async for i in AsyncIter(EXCLUDE_DOMAIN):
                x+= f"- `{i}`\n"
            return x
        return "No Excluded Domain"

    @property
    async def get_channels(self):
        x=''
        if CHANNELS:   
            async for i in AsyncIter(CHANNEL_ID):
                x+= f"~ `{i}`\n"
            return x
        return "Channels is set to False in heroku Var"

    @property
    async def get_admins(self):
        x=''
        async for i in AsyncIter(ADMINS):
            x+= f"~ `{i}`\n"
        return x
        
    @property
    async def header_text(self):
        if HEADER_TEXT:return HEADER_TEXT
        return "No Header Text"
        
    @property
    async def footer_text(self):
        if FOOTER_TEXT:return FOOTER_TEXT
        return "No Footer Text"

    @property
    async def get_username(self):
        return USERNAME

