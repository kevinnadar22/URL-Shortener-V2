from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


BATCH_MESSAGE = BATCH = """
This command is used to short or convert links from first to last posts

Make the bot as an admin in your channel

Command usage: `/batch [channel id or username]`

Ex: `/batch -100xxx`
"""

START_MESSAGE = '''Hello, {}

I'm a Bot to Convert Other MDisk Links to your MDisk Links or Short Other Links to Droplink.co Links by Using your API. 

Just Send me Any Post with Mdisk or Other Links. I will Convert Those Links Using Your API and Send them Back To You. I work in Channels too. 

Hit /help for more information about this Bot

Current Website Selected: **{}**
'''


HELP_MESSAGE = '''
Hey! My name is {firstname}. I am a Link Convertor and Shortener Bot, here to make your Work Easy and Help you to Earn more

I have lots of handy features, such as 

- Batch convert
- Channel Support
- Convert forwarded posts
- [Hyperlink](https://t.me/{username})
- Buttons convert support
- Include domains 
- Exclude domains
- Header and Footer Text support
- Replace Username

Helpful commands:

- /start: Starts me! You've probably already used this.
- /help: Sends this message; I'll tell you more about myself!
- /batch -100xxx: To short or convert all posts of your channel

If you have any bugs or questions on how to use me, have a look at my [website]({repo}), or contact to {owner}.

Below are some features I provide'''


ABOUT_TEXT = """
**My Details:**

`🤖 Name:` ** {} **
    
`📝 Language:` [Python 3](https://www.python.org/)
`🧰 Framework:` [Pyrogram](https://github.com/pyrogram/pyrogram)
`👨‍💻 Developer:` [Dev](t.me/ask_admin001)
`📢 Support:` [Talk Bot](https://t.me/t2linkspromotion_bot)
`🌐 Source Code:` [GitHub](https://github.com/T2links)
"""


METHOD_MESSAGE = """
Current Method: {method}
    
Methods Available:

> `mdlink` - Change all the links of the post to your MDisk account first and then short to droplink.co link.

> `droplink` - Short all the links of the post to droplink.co link directly.

> `mdisk` - Save all the links of the post to your Mdisk account.
    
To change method, choose it from the following options:
"""

CUSTOM_ALIAS_MESSAGE = """For custom alias, `[link] | [custom_alias]`, Send in this format

This feature works only in private mode only

Ex: https://t.me/example | Example"""


ADMINS_MESSAGE = """
List of Admins who has access to this Bot

{admin_list}
"""

OTHER_INFO_MESSAGE = """
**Current Method**: `{method}`

**Droplink API**: `{droplink_api}`

**MDisk API**: `{mdisk_api}`

**Included Domain**:
`{included_domain}`

**Excluded Domain**:
`{excluded_domain}`

**Source Code** - `{source_code}`

**Username** - `@{username}`

**Custom Caption**:

{header_text}

`(Original Caption)`

{footer_text}
"""

CHANNELS_LIST_MESSAGE = """
List of channels that have access to this Bot:

{channels}"""


HELP_REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Methods', callback_data=f'method_command'),
        InlineKeyboardButton('Batch', callback_data=f'cbatch_command'),
        
    ],

    [
        InlineKeyboardButton('Custom Alias', callback_data=f'alias_conf'),
        InlineKeyboardButton('Other', callback_data='other_info'),
        
    ],

    [
        InlineKeyboardButton('Admins', callback_data=f'admins_list'),
        InlineKeyboardButton('Channels', callback_data=f'channels_list'),
        
    ],

    [
        InlineKeyboardButton('Home', callback_data='start_command')
    ]
])


ABOUT_REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Home', callback_data=f'start_command'),
        InlineKeyboardButton('Help', callback_data=f'help_command')
    ],
    [
        InlineKeyboardButton('Close', callback_data='delete')
    ]
])

START_MESSAGE_REPLY_MARKUP  = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Help', callback_data=f'help_command'),
        InlineKeyboardButton('About', callback_data='about_command')
    ],
        [
        InlineKeyboardButton('Method', callback_data=f'method_command'),
        InlineKeyboardButton('Close', callback_data='delete')
    ],

])

METHOD_REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('MDLINK', callback_data=f'change_method#mdlink'),
        InlineKeyboardButton('Droplink', callback_data='change_method#droplink'),
        InlineKeyboardButton('Mdisk', callback_data='change_method#mdisk')
    ],
        [
        InlineKeyboardButton('Back', callback_data=f'help_command'),
        InlineKeyboardButton('Close', callback_data='delete')
    ],

])

BACK_REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Back', callback_data=f'help_command')
    ],

])
