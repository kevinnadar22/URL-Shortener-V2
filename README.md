# URL-Shortener-V2
Droplink URL Shortener and MDISK convertor

#### The Easy Way

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Required Variables <br> <br>

* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps) <br><br>
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps) <br><br>
* `ADMINS`: Your Telegram ID and ID of Users you want add as Admin. Separate each ID by comma.<br><br>
* `BOT_TOKEN`: Your bot token from @botfather<br><br>
* `METHOD`: Select your preferred METHOD between droplink or mdisk. Enter exactly droplink or mdisk in lowercase<br><br>
* `DROPLINK_API`:  Get your DROPLINK_KEY from https://droplink.co/member/tools/api. If METHOD is mdisk, Leave it to default<br><br>
* `MDISK_API`: Get your MDISK API KEY from https://t.me/VideoToolMoneyTreebot. If METHOD is droplink, Leave it to default<br><br>


## Optional Variables <br> <br>

* `CHANNELS`: Enter True if you want the bot to work in Channels also else Leave it as it is<br><br>
* `CHANNEL_ID`: Enter your Channel ID, Leave this to deafault if CHANNELS set to False<br><br>
* `EXCLUDE_DOMAIN`: Use this option if you wish to short every link on your website but exclude only the links from the given domains list. Separate each domain by comma, No space inbetween. Works only when mode is selected to droplink<br><br>
* `INCLUDE_DOMAIN`: Use this option if you want to short only links from the given domains list. Separate each domain by comma, No space inbetween. Works only when mode is selected to droplink<br><br>
* `FORWARD_MESSAGE`: Enter True if you want to edit forwarded message also in your channel. Entering True will delete the forwarded post in your channel and repost it with shorten link. Leave this to deafault if CHANNELS set to False<br><br>


## Bot Usage: <br><br>

* `Droplink` - This bot can short links from telegram text, photo, document and button messages to droplink links with custom alias support. This bot can edit posts in channels too. <br><br>

* `MDisk` - This bot will upload mdisk links to your account through API KEY. Can be used in channels too



