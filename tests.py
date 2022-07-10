
import re
caption = "https://t.me/vexample | f https://t.me/vexample | f"

regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))\s\|\s([a-zA-Z0-9_]){,30}"
custom_alias = re.match(regex, caption)

print(custom_alias.group(0))