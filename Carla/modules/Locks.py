from Carla import tbot
from telethon import Button, events
from . import is_admin, can_change_info

supported = ["all", "album", "audio", "bot", "button", "command", "contact", "document", "email", "emojigame", "forward", "forwardbot", "forwardchannel", "game", "gif", "inline", "invitelink", "location", "phone", "photo", "poll", "rtl", "sticker", "text", "url", "video", voicenote", "voice"]

ltext = """
The available locktypes are:
- all
- album
- audio
- bot
- button
- command
- comment
- contact
- document
- email
- emojigame
- forward
- forwardbot
- forwardchannel
- forwarduser
- game
- gif
- inline
- invitelink
- location
- phone
- photo
- poll
- rtl
- sticker
- text
- url
- video
- videonote
- voice
"""

@Cbot(pattern="^/locktypes ?(.*)")
async def _(event):
 if event.is_private:
   await event.respond(ltext)
 if event.is_group:
   if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("You need to be an admin to do this.")
   await event.reply(ltext)

@Cbot(pattern="^/lock ?(.*)")
async def _(event):
 if event.is_private:
   return #connect
 if not await can_change_info(event, event.sender_id):
   return
 args = event.pattern_match.group(1)
 if not args in supported:
      return await event.reply(f"Unknown lock types:\n- {args}\nCheck /locktypes!")
 
