# URL-Shortener-V2
Droplink URL Shortener and MDISK convertor

#### The Easy Way

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Required Variables

* `BOT_TOKEN`: Create a bot using [@BotFather](https://telegram.dog/BotFather), and get the Telegram API token.

* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `WEBSITE`: Any shortener website which you want to use. Ex. droplink.co
* `API_KEY`: API_KEY of the WEBSITE you want to use. Get this value from https://your_website/member/tools/api


## Bot Usage:

Just send me any post with link, I will send you the shorten link

You can use me in channel too 

Add your Channel ID in Heroku vars. Make me admin in your channel with edit permission. That's enough, now continue 
posting movies in channel I will edit all posts and add the shorten link

##### Custom Alias:

Send me a link to short a link with random alias.
For custom alias, [link] | [custom_alias], Send in this format

Ex: https://t.me/example | Example

### Commands

* /start - start message

* /batch - This command is used to short all links from the first post to last post in your channel. Make the bot as an 
admin in your channel.

Command usage: /batch [channel id or username]

* /help - The current command

* /about - About this bot
