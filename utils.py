import re
import json
import aiohttp
import requests
from pyrogram import Client
from config import *
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyshorteners

async def main_convertor_handler(c:Client, message:Message, type:str, edit_caption:bool=False):

	if message.text:
		caption = message.text.markdown

	else:
		caption = message.caption.markdown

	user_method = type

# Checking if the user has set his method or not. If not, it will reply with a message.
	if user_method is None:
		return await message.reply(text="Set your /method first")

# A dictionary which contains the methods to be called.
	METHODS = {
		"mdisk": replace_mdisk_link,
		"droplink": replace_link,
		"mdlink": mdisk_droplink_convertor
	}

	# Replacing the username with your username.
	caption = await replace_username(caption)

	method_func = METHODS[user_method]


	if message.reply_markup:  # reply markup - button post
		txt = str(caption)
		reply_markup = json.loads(str(message.reply_markup))
		buttsons = []
		for i, markup in enumerate(reply_markup["inline_keyboard"]):
			buttons = []
			for j in markup:
				text = j["text"]
				url = j["url"]
				url = await method_func(url)
				regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
				url = re.findall(regex, url)
				button = InlineKeyboardButton(text, url=url[0][0])
				buttons.append(button)
			buttsons.append(buttons)

		txt = await method_func(txt)

		if message.text:
			if edit_caption:
				return await message.edit(str(txt), reply_markup=InlineKeyboardMarkup(buttsons), )

			await message.reply(text=str(txt), reply_markup=InlineKeyboardMarkup(buttsons), )

		elif message.caption:
			if edit_caption:
				return await message.edit_caption(str(txt), reply_markup=InlineKeyboardMarkup(buttsons),)

			if message.photo:
				await message.reply_photo(photo=message.photo.file_id, caption=str(txt),
											reply_markup=InlineKeyboardMarkup(buttsons),
											)
			elif message.document:
				await message.reply_document(document=message.document.file_id, caption=str(txt),
												reply_markup=InlineKeyboardMarkup(buttsons),
												)

	elif message.text:
		text = str(caption)
		if user_method == "droplink" and "|" in text:
			alias = text.split('|')[1].replace(" ", "")
			if len(text) < 30:
				links = re.findall(r'https?://[^\s]+', text)[0]
				link = await method_func(links, alias) 
				await message.reply_text(str(link))
				return

		link = await method_func(text)

		if edit_caption:
			return await message.edit(str(link))

		await message.reply_text(str(link))

	elif message.photo:  # for media messages
		fileid = message.photo.file_id
		text = str(caption)
		link = await method_func(text)

		if edit_caption:
			return await message.edit_caption(str(link))

		await message.reply_photo(fileid, caption=str(link))

# For document messages.
	elif message.document:  
		fileid = message.document.file_id
		text = str(caption)
		link = await method_func(text)

		if edit_caption:
			return await message.edit_caption(link)

		await message.reply_document(fileid, caption=str(link))


####################  droplink  ####################
async def get_shortlink(link, x=""):
	https = link.split(":")[0]
	if "http" == https:
		https = "https"
		link = link.replace("http", https)
	url = f'https://droplink.co/api'
	params = {'api': DROPLINK_API,
			  'url': link,
			  'alias': x
			  }

	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
				data = await response.json()
				if data["status"] == "success":
					return data['shortenedUrl']
				else:
					return f"Error: {data['message']}"

	except Exception as e:
		print(e)
		links = f'https://droplink.co/st?api={DROPLINK_API}&url={link}'
		return await tiny_url_main(links)


async def replace_link(text, x=""):
	links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
	for link in links:
		link = link.replace(")", "")
		if INCLUDE_DOMAIN:
			include = INCLUDE_DOMAIN.split(',')
			domain = [domain.strip() for domain in include]
			if any(i in link for i in domain):
				short_link = await get_shortlink(link, x)
				text = text.replace(link, short_link)

		elif EXCLUDE_DOMAIN:
			exclude = EXCLUDE_DOMAIN.split(',')
			domain = [domain.strip() for domain in exclude]
			if any(i in link for i in domain):
				pass
			else:
				short_link = await get_shortlink(link, x)

				text = text.replace(link, short_link)

		else:
			short_link = await get_shortlink(link, x)

			text = text.replace(link, short_link)

	return text


####################  Mdisk  ####################

async def get_mdisk(link):
	url = 'https://diskuploader.mypowerdisk.com/v1/tp/cp'
	param = {'token': MDISK_API, 'link': link
			 }
	res = requests.post(url, json=param)
	try:
		shareLink = res.json()
		link = shareLink["sharelink"]
	except Exception as e:
		print(e)

	return link


async def replace_mdisk_link(text):
	links = re.findall(r'https?://mdisk.me[^\s]+', text)
	for link in links:
		link = link.replace(")", "")
		mdisk_link = await get_mdisk(link)
		text = text.replace(link, mdisk_link)
	return text


####################  Mdisk and Droplink  ####################

async def mdisk_droplink_convertor(text):
	links = await replace_mdisk_link(text)
	links = await replace_link(links, x="")
	return links

####################  Mdisk and Droplink Reply Markup ####################

async def mdisk_droplink_convertor_reply_markup(text):
	links = await replace_mdisk_link(text)
	links = await replace_link(links, x="")
	return links

####################  Replace Username  ####################
async def replace_username(text):
	if USERNAME:
		usernames = re.findall("([@#][A-Za-z0-9_]+)", text)
		for i in usernames:
			text = text.replace(i, f"@{USERNAME}")
	return text
	

#####################  Extract all urls in a string ####################
async def extract_link(string):
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
	return urls



# Incase droplink server fails, bot will return https://droplink.co/st?api={DROPLINK_API}&url={link} 

# TinyUrl 
async def tiny_url_main(url):
	s = pyshorteners.Shortener()
	return s.tinyurl.short(url)