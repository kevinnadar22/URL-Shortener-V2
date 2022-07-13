import re
import json
import aiohttp
import requests
from pyrogram import Client
from config import *
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyshorteners
from pyrogram.types import InputMediaPhoto

async def main_convertor_handler(message:Message, type:str, edit_caption:bool=False):
	caption = None



	if message.text:
		caption = message.text.html
	elif message.caption:
		caption = message.caption.html


	# Checking if the message has any link or not. If it doesn't have any link, it will return.
	if len(await extract_link(caption)) <=0 and not message.reply_markup:
		return

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


	# Getting the function for the user's method
	method_func = METHODS[user_method] 

	# converting urls
	shortenedText = await method_func(caption)

	# converting reply_markup urls
	reply_markup = await reply_markup_handler(message, method_func)

	# Adding header and footer
	shortenedText = f"{HEADER_TEXT}\n{shortenedText}\n{FOOTER_TEXT}"

	# Used to get the file_id of the media. If the media is a photo and BANNER_IMAGE is set, it will
	# replace the file_id with the BANNER_IMAGE.
	if message.media:
		medias = getattr(message, message.media.value)
		fileid = medias.file_id
		if message.photo and BANNER_IMAGE:
			fileid = BANNER_IMAGE
			if edit_caption:
				fileid = InputMediaPhoto(BANNER_IMAGE, caption=shortenedText)
		

	if message.text:
		if user_method in ["droplink", "mdlink"] :
			regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))\s\|\s([a-zA-Z0-9_]){,30}"
			custom_alias = re.match(regex, caption)

			if custom_alias:
				custom_alias = custom_alias.group(0).split('|')
				alias = custom_alias[1].strip()
				url = custom_alias[0].strip()
				shortenedText = await method_func(url, alias)
		
		if edit_caption:
			return await message.edit(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup)
		return await message.reply(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup)

	elif message.media:

		if edit_caption:
			if BANNER_IMAGE and message.photo:
				return await message.edit_media(media=fileid)

			return await message.edit_caption(shortenedText, reply_markup=reply_markup)

		if message.document:
			return await message.reply_document(fileid, caption=shortenedText, reply_markup=reply_markup)

		
		elif message.photo:
			return await message.reply_photo(fileid, caption=shortenedText, reply_markup=reply_markup)



# Reply markup 
async def reply_markup_handler(message:Message, method_func):
	if message.reply_markup:
		reply_markup = json.loads(str(message.reply_markup))
		buttsons = []
		for markup in reply_markup["inline_keyboard"]:
			buttons = []
			for j in markup:
				text = j["text"]
				url = j["url"]
				url = await method_func(url)
				button = InlineKeyboardButton(text, url=url)
				buttons.append(button)
			buttsons.append(buttons)
		reply_markup = InlineKeyboardMarkup(buttsons)
		return reply_markup


####################  droplink  ####################
async def get_shortlink(link, x=""):
	https = link.split(":")[0]
	if "http" == https:
		https = "https"
		link = link.replace("http", https)
	url = f'https://shorturllink.in/api'
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
		links = f'https://urlsopen.com/st?api={DROPLINK_API}&url={link}'
		return await tiny_url_main(links)


async def replace_link(text, x=""):
	links = await extract_link(text)
	for link in links:
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

async def mdisk_droplink_convertor(text, alias=""):
	links = await replace_mdisk_link(text)
	links = await replace_link(links, x=alias)
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
	regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
	urls = re.findall(regex, string)
	return ["".join(x) for x in urls]


# Incase droplink server fails, bot will return https://droplink.co/st?api={DROPLINK_API}&url={link} 

# TinyUrl 
async def tiny_url_main(url):
	s = pyshorteners.Shortener()
	return s.tinyurl.short(url)
