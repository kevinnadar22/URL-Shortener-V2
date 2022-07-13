# URL Shortener Bot V2

<p align="center">

![Fork](https://img.shields.io/github/forks/kevinnadar22/URL-Shortener-V2?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/kevinnadar22/URL-Shortener-V2?color=%23&style=for-the-badge)
![License](https://img.shields.io/github/license/kevinnadar22/URL-Shortener-V2?style=for-the-badge)
![Issues](https://img.shields.io/github/issues/kevinnadar22/URL-Shortener-V2?style=for-the-badge)

</p>

---

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/kevinnadar22/URL-Shortener-V2">
    <img src="https://i.ibb.co/1mwchh9/Screenshot-2022-07-08-at-11-06-34-AM.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">URL Shortener Bot V2</h3>

  <p align="center">
    A Shortener and Convertor Bot
    <br />
    ·
    <a href="https://www.telegram.dog/ask_admin001">Report Bug</a>
    ·
    <a href="https://github.com/kevinnadar22/URL-Shortener-V2#features">Features</a>
    ·
    <a href="https://github.com/kevinnadar22/URL-Shortener-V2#deploy">Deploy</a>
    ·
    <a href="https://github.com/kevinnadar22/URL-Shortener-V2#required-variables">Variables</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#description">Description</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#commands">Commands</a></li>
    <li>
        <a href="#about">About</a>
        <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#required-variables">Required Variables</a></li>
        <li><a href="#optional-variables">Optional Variables</a></li>
      </ul>
      </li>
    <li><a href="#deploy">Deploy</a></li>
    <li><a href="#tech-stack">Tech Stack</a></li>
    <li><a href="#support">Support</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
    <li><a href="#credits">Credits</a></li>
  </ol>
</details>


---

## Description

__This Is Just An Simple Advance Shortener and Converter Bot Completely Rewritten Version Of [URL Shortener](https://github.com/t2links/URL-Shortener-bot)__

__Just Send Any Link To Short. It Will Short To Droplink Link or Save it to your MDisk Account__


## Usage

**__How To Use Me!?__**

* -> Send any link or post of links

* -> Add me to your channel as admin with full previlages to convert channel's post

## Commands

```
/start - Check if I'm alive
/help - Help Command
/about - About Command
/method - To set your preferred method
/batch -100XX - to convert link for multiple posts
```

## About 

### Features

- [x] Droplink Shortener
- [x] Mdisk Convertor
- [x] Channels Support
- [x] Batch Support
- [x] Multiple Methods Available
- [x] [Hyperlink Support](https://example.com/)


### Required Variables
* `BOT_TOKEN`: Create a bot using [@BotFather](https://telegram.dog/BotFather), and get the Telegram API token.
* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `DROPLINK_API`: Your [Droplink API](https://droplink.co/member/tools/api)
* `MDISK_API`: Your [Mdisk API](https://t.me/VideoToolMoneyTreebot)
* `ADMINS`: ID of Admins. Separate multiple Admins by comma
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Get this value from [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)
* `DATABASE_NAME`: Name of the database in [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)


### Optional Variables
* `CHANNELS`: Set True if you want channels to be available for converting 
* `CHANNEL_ID`: Your channel list to convert posts. Seperate channels list by space
* `INCLUDE_DOMAIN`: Use this option if you want to short only links from the following domains list.
* `EXCLUDE_DOMAIN`: Use this option if you wish to short every link on your channel but exclude only the links from the following domains list.
* `FORWARD_MESSAGE`: Set True if you want forwarded posts to be converted in your channels
* `USERNAME`: Your Channel username without @ to replace other usernames in posts

### Extra Variables
* `SOURCE_CODE`: Your Github repo
* `HEADER_TEXT`: This text will be added on top of every post caption or text. [HTML](https://docs.pyrogram.org/topics/text-formatting#html-style) and [Markdown](https://docs.pyrogram.org/topics/text-formatting#markdown-style) Supported. See More
* `FOOTER_TEXT`: This text will be added on bottom of every post caption or text. [HTML](https://docs.pyrogram.org/topics/text-formatting#html-style) and [Markdown](https://docs.pyrogram.org/topics/text-formatting#markdown-style) Supported. See More
* `BANNER_IMAGE`: All images of media posts will be replaced with this image. Enter [telegraph](https://t.me/AVTelegraphBot) or any direct image links. 
* `WELCOME_IMAGE`: Enter [telegraph](https://t.me/AVTelegraphBot) or any direct image links. 

**PR's Are Very Welcome**


## Deploy 


You can deploy this bot anywhere.


|                                                                                                                 | Name              | Deploy        |
| --------------------------------------------------------------------------------------------------------------- | ----------------- | ------------- | 
| [![Heroku](assets/img/heroku.png)](https://heroku.com)                                                          | Heroku            | [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/kevinnadar22/URL-Shortener-V2)                          |
| ![VPS](assets/img/vps.png) | VPS | [see guide](/guides/vps.md) |



## Tech Stack

**Language:** [Python](https://www.python.org/) 3.9.9

**Library:** [Pyrogram](https://github.com/pyrogram/pyrogram) 2.0.30


## Support   

Contact Our [DEV](https://www.telegram.dog/ask_admin001) For Support/Assistance    
   
Report Bugs, Give Feature Requests There..   
Do Fork And Star The Repository If You Liked It.

## Disclaimer

[![GNU Affero General Public License v3.0](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html#header)    
Licensed under [GNU AGPL v3.0.](https://github.com/CrazyBotsz/Adv-Auto-Filter-Bot-V2/blob/main/LICENSE)
Selling The Codes To Other People For Money Is *Strictly Prohibited*.


## Credits
 - [Thanks To Me](https://github.com/Kevinnadar22)
