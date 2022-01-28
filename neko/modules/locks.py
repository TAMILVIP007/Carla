from telethon import events
from telethon.tl.types import (
    Channel,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
    MessageEntityBankCard,
    MessageEntityBotCommand,
    MessageEntityEmail,
    MessageEntityPhone,
    MessageEntityUrl,
    MessageMediaDice,
    MessageMediaDocument,
    MessageMediaGame,
    MessageMediaGeo,
    MessageMediaGeoLive,
    MessageMediaInvoice,
    MessageMediaPhoto,
    MessageMediaPoll,
    MessageMediaWebPage,
    PeerChannel,
    PeerUser,
    User,
)

from .. import CMD_HELP, tbot
from ..utils import Cbot
from . import can_change_info
from . import db as database
from . import is_admin
from .mongodb import locks_db as db

approve_d = database.approve_d


@Cbot(pattern="^/lock ?(.*)")
async def lock_item(event):
    if (
        event.text.startswith("+locks")
        or event.text.startswith("/locks")
        or event.text.startswith("!locks")
        or event.text.startswith("?locks")
        or event.text.startswith("+locktypes")
        or event.text.startswith("/locktypes")
        or event.text.startswith("?locktypes")
        or event.text.startswith("!locktypes")
    ):
        return
    if event.is_private:
        return await event.reply("This command is made to be used in group chats.")
    if (
        event.is_group
        and event.from_id
        and not await can_change_info(event, event.sender_id)
    ):
        return
    if not event.pattern_match.group(1):
        return await event.reply("You haven't specified a type to lock.")
    try:
        lock_items = event.text.split(None, 1)[1]
    except IndexError:
        return await event.reply("You haven't specified a type to lock.")
    locks = lock_items.split(None)
    av_locks = db.all_locks
    lock_s = [lock for lock in locks if lock.lower() in av_locks]
    if "all" in lock_s:
        db.lock_all(event.chat_id)
        await event.reply("Locked `all`")
        try:
            await tbot.edit_permissions(event.chat_id, send_messages=False)
        except Exception as e:
            print(e)
        return
    if not lock_s:
        await event.reply(f"Unknown lock types:- {lock_items}\nCheck /locktypes!")
    else:
        text = "Locked"
        if len(lock_s) == 1:
            text += f" `{lock_s[0]}`"
        else:
            for qp, i in enumerate(lock_s, start=1):
                text += f" `{i}`" if len(lock_s) == qp - 1 else f" `{i}`,"
        await event.reply(text)
    for lock in lock_s:
        db.add_lock(event.chat_id, lock.lower())
    if "text" in lock_s:
        try:
            await tbot.edit_permissions(event.chat_id, send_messages=False)
        except:
            pass
    if "media" in lock_s:
        try:
            await tbot.edit_permissions(event.chat_id, send_media=False)
        except:
            pass
    if "inline" in lock_s:
        try:
            await tbot.edit_permissions(event.chat_id, send_inline=False)
        except:
            pass


@Cbot(pattern="^/locktypes")
async def lock_types(event):
    main_txt = "The avaliable lock types are:"
    av_locks = db.all_locks
    for x in av_locks:
        main_txt += "\n- " + x
    await event.reply(main_txt)


@Cbot(pattern="^/locks")
async def locks(event):
    if not await can_change_info(event, event.sender_id):
        return
    av_locks = db.all_locks
    _final = "These are the current lock settings:"
    locked = db.get_locks(event.chat_id) or []
    for x in av_locks:
        _mode = "true" if x in locked else "false"
        _final = _final + "\n- " + x + " = " + _mode
    await event.reply(_final)


@Cbot(pattern="^/unlock ?(.*)")
async def unlock_item(event):
    if event.is_private:
        return await event.reply("This command is made to be used in group chats.")
    if (
        event.is_group
        and event.from_id
        and not await can_change_info(event, event.sender_id)
    ):
        return
    if not event.from_id:
        return await a_locks(event, "unlock")
    if not event.pattern_match.group(1):
        return await event.reply("You haven't specified a type to unlock.")
    try:
        unlock_items = event.text.split(None, 1)[1]
    except IndexError:
        return await event.reply("You haven't specified a type to unlock.")
    unlocks = unlock_items.split(None)
    av_locks = db.all_locks
    unlock_s = [unlock for unlock in unlocks if unlock.lower() in av_locks]
    if "all" in unlock_s:
        db.unlock_all(event.chat_id)
        await event.reply("Unlocked `all`")
        try:
            await tbot.edit_permissions(event.chat_id, send_messages=True)
        except:
            pass
        return
    if not unlock_s:
        await event.reply(f"Unknown lock types:- {unlock_items}\nCheck /locktypes!")
    else:
        text = "Unlocked"
        if len(unlock_s) == 1:
            text += f" `{unlock_s[0]}`"
        else:
            for i in unlock_s:
                text += f" `{i}`,"
        await event.reply(text)
    for lock in unlock_s:
        db.remove_lock(event.chat_id, lock.lower())
    if "text" in unlock_s:
        try:
            await tbot.edit_permissions(event.chat_id, send_messages=True)
        except:
            pass
    if "media" in unlock_s:
        try:
            await tbot.edit_permissions(event.chat_id, send_media=True)
        except:
            pass
    if "inline" in unlock_s:
        try:
            await tbot.edit_permissions(event.chat_id, send_inline=True)
        except:
            pass


@tbot.on(events.NewMessage())
async def locks(event):
    if event.is_private:
        return
    if not event.from_id:
        return
    if not isinstance(event.sender, User):
        return
    if not event.chat.admin_rights:
        return
    if not event.chat.admin_rights.delete_messages:
        return
    if approve_d.find_one({"user_id": event.sender_id, "chat_id": event.chat_id}):
        return
    locked = db.get_locks(event.chat_id)
    if not locked or len(locked) == 0:
        return
    trigg = await lock_check(event, locked)
    if trigg and not await is_admin(event.chat_id, event.sender_id):
        await event.delete()


async def lock_check(event, locked):
    if "sticker" in locked and event.sticker:
        return True
    if "gif" in locked and event.gif:
        return True
    if (
        "document" in locked
        and event.media
        and isinstance(event.media, MessageMediaDocument)
        and event.media.document.mime_type
        not in [
            "image/webp",
            "application/x-tgsticker",
            "image/jpeg",
            "audio/ogg",
            "audio/m4a",
            "audio/mp3",
            "video/mp4",
        ]
    ):
        return True
    if (
        "location" in locked
        and event.media
        and isinstance(event.media, (MessageMediaGeo, MessageMediaGeoLive))
    ):
        return True
    if (
        "phone" in locked
        and event.message.entities
        and isinstance(event.message.entities[0], MessageEntityPhone)
    ):
        return True
    if (
        "email" in locked
        and event.message.entities
        and isinstance(event.message.entities[0], MessageEntityEmail)
    ):
        return True
    if (
        "command" in locked
        and event.message.entities
        and isinstance(event.message.entities[0], MessageEntityBotCommand)
    ):
        return True
    if (
        "url" in locked
        and event.message.entities
        and isinstance(event.message.entities[0], MessageEntityUrl)
    ):
        return True
    if "invitelink" in locked and event.text and "t.me/" in event.text:
        return True
    if (
        "poll" in locked
        and event.media
        and isinstance(event.media, MessageMediaPoll)
    ):
        return True
    if (
        "photo" in locked
        and event.media
        and isinstance(event.media, MessageMediaPhoto)
    ):
        return True
    if (
        "videonote" in locked
        and event.media
        and isinstance(event.media, MessageMediaDocument)
        and event.media.document.mime_type == "video/mp4"
    ):
        return True
    if (
        "video" in locked
        and event.media
        and isinstance(event.media, MessageMediaDocument)
        and isinstance(
            event.media.document.attributes[0], DocumentAttributeVideo
        )
    ):
        return True
    if (
        "voice" in locked
        and event.media
        and isinstance(event.media, MessageMediaDocument)
        and isinstance(
            event.media.document.attributes[0], DocumentAttributeAudio
        )
        and event.media.document.attributes[0].voice
    ):
        return True
    if (
        "audio" in locked
        and event.media
        and isinstance(event.media, MessageMediaDocument)
        and isinstance(
            event.media.document.attributes[0], DocumentAttributeAudio
        )
    ):
        return True
    if "bot" in locked and event.sender.bot:
        return True
    if "button" in locked and event.reply_markup:
        return True
    if (
        "game" in locked
        and event.media
        and isinstance(event.media, MessageMediaGame)
    ):
        return True
    if (
        "contact" in locked
        and event.media
        and isinstance(event.media, MessageMediaDice)
    ):
        return True
    if "forward" in locked and event.fwd_from:
        return True
    if (
        "emojigame" in locked
        and event.media
        and isinstance(event.media, MessageMediaDice)
    ):
        return True
    if (
        "forwardchannel" in locked
        and event.fwd_from
        and event.fwd_from.from_id
        and isinstance(event.fwd_from.from_id, (PeerChannel, Channel))
    ):
        return True
    if (
        "forwarduser" in locked
        and event.fwd_from
        and event.fwd_from.from_id
        and isinstance(event.fwd_from.from_id, PeerUser)
    ):
        return True
    if (
        "preview" in locked
        and event.media
        and isinstance(event.media, MessageMediaWebPage)
    ):
        return True
    if (
        "forwardbot" in locked
        and event.fwd_from
        and event.fwd_from.from_id
        and event.sender.bot
    ):
        return True
    if (
        "invoice" in locked
        and event.media
        and isinstance(event.media, MessageMediaInvoice)
    ):
        return True
    if "comment" in locked:
        return False
    if "card" in locked and event.message.entities:
        for x in range(len(event.message.entities)):
            if isinstance(event.message.entities[x], MessageEntityBankCard):
                return True
    return False


# --------Album Lock---------
@tbot.on(events.Album())
async def album(e):
    if e.is_private:
        return
    if not isinstance(e.sender, User):
        return
    if not e.chat.admin_rights:
        return
    if not e.chat.admin_rights.delete_messages:
        return
    if approve_d.find_one({"user_id": e.sender_id, "chat_id": e.chat_id}):
        return
    locked = db.get_locks(e.chat_id)
    if not locked or len(locked) == 0:
        return
    if "album" in locked and not await is_admin(e.chat_id, e.sender_id):
        await e.delete()


__name__ = "locks"
__help__ = """
Here is the help for **Locks** module:

The locks module allows you to lock away some common items in the telegram world; the bot will automatically delete them!

**Admin commands:**
-> /lock <item(s)>: Lock one or more items. Now, only admins can use this type!
-> /unlock <item(s)>: Unlock one or more items. Everyone can use this type again!
-> /locks: List currently locked items.
-> /lockwarns <yes/no/on/off>: Enabled or disable whether a user should be warned when using a locked item.
-> /locktypes: Show the list of all lockable items.

**Examples:**
- Lock stickers with:
-> /lock sticker
- You can lock/unlock multiple items by chaining them:
-> /lock sticker photo gif video
"""

CMD_HELP.update({__name__: [__name__, __help__]})
