from Carla import tbot, OWNER_ID
from . import ELITES, can_change_info, is_admin
from Carla.events import Cbot
import os, re
import Carla.modules.sql.blacklist_sql as sql

@Cbot(pattern="^/addblocklist ?(.*)")
async def _(event):
 if event.is_private:
     return #connect
 if not await can_change_info(event, event.sender_id):
     return
 if event.reply_to_msg_id:
     msg = await event.get_reply_message()
     trigger = msg.message
 elif event.pattern_match.group(1):
     trigger = event.pattern_match.group(1)
 else:
     return await event.reply("You need to provide a blocklist trigger!\neg: `/addblocklist the admins suck`.")
 text = "Added blocklist filter '{}'!".format(trigger)
 await event.respond(text)
 sql.add_to_blacklist(event.chat_id, trigger)

@Cbot(pattern="^/addblacklist ?(.*)")
async def _(event):
 if event.is_private:
     return #connect
 if not await can_change_info(event, event.sender_id):
     return
 if event.reply_to_msg_id:
     msg = await event.get_reply_message()
     trigger = msg.message
 elif event.pattern_match.group(1):
     trigger = event.pattern_match.group(1)
 else:
     return await event.reply("You need to provide a blocklist trigger!\neg: `/addblocklist the admins suck`.")
 text = "Added blocklist filter '{}'!".format(trigger)
 await event.respond(text)
 sql.add_to_blacklist(event.chat_id, trigger)
 
@Cbot(pattern="^/(blocklist|blacklist)$")
async def _(event):
 if event.is_private:
     return #connect
 if not await is_admin(event.chat_id, event.sender_id):
     return await event.reply("You need to be an admin to do this.")
 all_blacklisted = sql.get_chat_blacklist(event.chat_id)
 if len(all_blacklisted) == 0:
    text = 'No blocklist filters active in {}!'.format(event.chat.title)
 else:
    text = 'The following blocklist filters are currently active in {}:'.format(event.chat.title)
    for i in all_blacklisted:
          text += f"\n- `{i}`"
 await event.reply(text)

@Cbot(pattern="^/rmblacklist ?(.*)")
async def _(event):
 if event.is_private:
     return #connect
 if not await can_change_info(event, event.sender_id):
     return
 args = event.pattern_match.group(1)
 if not args:
  return await event.reply("You need to specify the blocklist filter to remove")
 d = sql.rm_from_blacklist(event.chat_id, args)
 if d:
   text = "I will no longer blocklist '{}'.".format(args)
 else:
   text = "`{args}` has not been blocklisted, and so could not be stopped. Use the /blocklist command to see the current blocklist."
 await event.reply(text)
