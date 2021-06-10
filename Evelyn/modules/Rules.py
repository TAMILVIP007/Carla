from Evelyn.events import Cbot
import Evelyn.modules.sql.rules_sql as sql
from . import can_change_info

pos = ["on", "yes", "u"]
neg = ["off", "no", "n"]


@Cbot(pattern="^/privaterules ?(.*)")
async def pr(event):
    if event.is_private:
        return await event.reply("This command is made to be used in group chats, not in pm!")
    if event.is_group and event.from_id:
        if not await can_change_info(event, event.sender_id):
           return
    args = event.pattern_match.group(1)
    if not args:
        mode = sql.get_private(event.chat_id)
        if mode:
            await event.reply("Use of /rules will send the rules to the user's PM.")
        else:
            await event.reply(
                f"All /rules commands will send the rules to {event.chat.title}."
            )
    elif args in pos:
        await event.reply("Use of /rules will send the rules to the user's PM.")
        sql.set_private_rules(event.chat_id, True)
    elif args in neg:
        await event.reply(
            f"All /rules commands will send the rules to {event.chat.title}."
        )
        sql.set_private_rules(event.chat_id, False)
    else:
        await event.reply("I only understand the following: yes/no/on/off")


@Cbot(pattern="^/setrules ?(.*)")
async def set_r(event):
 if event.text.startswith(".setrulesbutton") or event.text.startswith("?setrulesbutton") or event.text.startswith("!setrulesbutton") or event.text.startswith("!setrulesbutton"):
    return
 if event.is_private:
   return await event.reply("This command is made to be used in group chats, not in pm!")
 if event.is_group and event.from_id:
   if not await can_change_info(event, event.sender_id):
     return
 if not event.reply_to and not event.pattern_match.group(1):
   return await event.reply("You need to give me rules to set!")
 elif event.reply_to:
   r_text = ""
   r_msg = await event.get_reply_message()
   if r_msg.text:
     r_text = r_msg.text
   if r_msg.reply_markup:
     buttons = get_reply_msg_btns_text(r_msg)
     r_text = r_text + str(buttons)
   if r_msg.media and not r_msg.text:
     return await event.reply("You need to give me rules to set!")
 elif event.pattern_match.group(1):
     r_text = event.text.split(None, 1)[1]
 await event.reply("New rules for {} set successfully!".format(event.chat.title))
 sql.set_rules(event.chat_id, r_text)
 
@Cbot(pattern="^/resetrules$")
async def reset_rules(event):
 if event.text.startswith(".resetrulesbutton") or event.text.startswith("?resetrulesbutton") or event.text.startswith("!resetrulesbutton") or event.text.startswith("!resetrulesbutton"):
    return
 if event.is_private:
   return await event.reply("This command is made to be used in group chats, not in pm!")
 if event.is_group and event.from_id:
   if not await can_change_info(event, event.sender_id):
     return
 await event.reply(f"Rules for {event.chat.title} were successfully cleared!")
 sql.set_rules(event.chat_id, "")

r_btn = """
The rules button will be called:
`{}`

To change the button name, try this command again followed by the new name
"""

@Cbot(pattern="^/setrulesbutton ?(.*)")
async def s_r_b(event):
 if event.is_private:
   return await event.reply("This command is made to be used in group chats, not in pm!")
 if event.is_group and event.from_id:
   if not await can_change_info(event, event.sender_id):
     return
 args = event.pattern_match.group(1)
 if not args:
   btn = sql.get_button(event.chat_id)
   await event.reply(r_btn.format(btn))
 elif len(args) > 100:
   r_over = "Your new rules button name is too long; please make it shorter (under 100 characters)."
   await event.reply(r_over)
 else:
   await event.reply("Updated the rules button name!")
   sql.set_button(event.chat_id, str(args))

@Cbot(pattern="^/resetrulesbutton$")
async def r_s_r_b(event):
 if event.is_private:
   return await event.reply("This command is made to be used in group chats, not in pm!")
 if event.is_group and event.from_id:
   if not await can_change_info(event, event.sender_id):
     return
 await event.reply("Reset the rules button name to default")
 sql.set_button(event.chat_id, "Rules")


   
