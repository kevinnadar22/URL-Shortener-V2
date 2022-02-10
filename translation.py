BATCH = """This command is used to short all links in your channel. Make the bot as an admin in your channel.\n\n 
Command usage: `/batch -100xxxx or @xxx`"""

START_MESSAGE = '''Hi, {}

I'm a bot to short your links to droplink.co or mdisk.me

Current Website Selected: {}

Hit /help for how to use

'''


HELP_MESSAGE = '''
<i>Problem: This bot can't short links which are in this format 👉 [Unsupported Link](t.me/example)</i>

★ Bot Usage:

Just send me any post with link, I will send you the shorten link

You can use me in channel too 

* Add your Channel ID in Heroku vars. Make me admin in your channel with edit permission. That's enough, now continue 
posting movies in channel I will edit all posts and add the shorten link

★ Custom Alias:

Send me a link to short a link with random alias.
For custom alias, <code>[link] | [custom_alias]</code>, Send in this format\n
Ex: https://t.me/example | Example

★ Commands

/start - start message

/batch - This command is used to short all links from the first post to last post in your channel. Make the bot as an 
admin in your channel.\n\nCommand usage: `/batch [channel id or username]`

/help - The current command

/about - About this bot
'''

ABOUT_TEXT = """
**My Details:**
🤖 Name: {}
    
📝 Language: [Python 3](https://www.python.org/)
🧰 Framework: [Pyrogram](https://github.com/pyrogram/pyrogram)
👨‍💻 Developer: [Dev](t.me/ask_admin001)
📢 Support: [Talk Bot](https://t.me/t2linkspromotion_bot)
🌐 Source Code: [GitHub](https://github.com/T2links)
"""