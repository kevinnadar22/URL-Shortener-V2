# URL-Shortener-V2
Droplink URL Shortener and MDISK convertor

#### The Easy Way

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Required Variables

* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `ADMINS`: Your Telegram ID and ID of Users you want add as Admin. Separate each ID by comma.
* `BOT_TOKEN`: Your bot token from @botfather
* `MODE`: Select your preferred mode between droplink or mdisk. Enter exactly droplink or mdisk in lowercase
* `DROPLINK_KEY`:  Get your DROPLINK_KEY from https://droplink.co/member/tools/api. If MODE is mdisk, Leave it to default
* `MDISK_KEY`: Enter your MDISK API KEY only if mode is selected to mdisk. Get your MDISK API KEY from https://t.me/VideoToolMoneyTreebot


## Optional Variables

* `CHANNELS`: Enter True if you want the bot to work in Channels also else Leave it as it is
* `CHANNEL_ID`: Enter your Channel ID, Leave this to deafault if CHANNELS set to False
* `EXCLUDE_DOMAIN`: Use this option if you wish to short every link on your website but exclude only the links from the given domains list. Separate each domain by comma, No space inbetween. Works only when mode is selected to droplink
* `INCLUDE_DOMAIN`: Use this option if you want to short only links from the given domains list. Separate each domain by comma, No space inbetween. Works only when mode is selected to droplink
* `FORWARD_MESSAGE`: Enter True if you want to edit forwarded message also in your channel. Entering True will delete the forwarded post in your channel and repost it with shorten link. Leave this to deafault if CHANNELS set to False


## Bot Usage:

DROPLINK - This BOT can short links from telegram text, photo, document and button messages to droplink links with custom alias support. This bot can edit postes in channels also.

MDISK - This bot will upload mdisk links to your account through API ID. Can be used in channels



