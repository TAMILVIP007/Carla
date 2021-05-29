import asyncio
import math
import re
import shlex
import time
from random import choice, randint
from typing import Tuple

from captcha.image import ImageCaptcha
from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient
from telethon import Button, events
from telethon.errors.rpcerrorlist import UserNotParticipantError

from Evelyn import BOT_ID, MONGO_DB_URI, OWNER_ID, tbot
from Evelyn.modules.sql.chats_sql import add_chat, is_chat

SUDO_USERS = []
ELITES = []

ELITES.append(OWNER_ID)

# DB
client = MongoClient(MONGO_DB_URI)
db = client["Rylee"]

# Add chat to DB
@tbot.on(events.ChatAction)
async def handler(event):
    if event.user_added:
        if event.user_id == BOT_ID:
            if not is_chat(event.chat_id):
                add_chat(event.chat_id)
            await event.respond(
                "Heya :-D Now leave your group on my hands and let me manage it. If you need any help, head to @EvelynSupport."
            )


async def can_promote_users(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.reply("Only admins can execute this command!")
        return False
    if not perm.add_admins:
        await event.reply(
            "You are missing the following rights to use this command: CanPromoteUsers."
        )
        return False
    return True


async def cb_can_promote_users(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.answer("You need to be an admin to do this.")
        return False
    if not perm.add_admins:
        await event.edit(
            "You are missing the following rights to use this command: CanPromoteUsers."
        )
        return False
    return True


async def cb_can_ban_users(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.answer("You need to be an admin to do this.")
        return False
    if not perm.ban_users:
        await event.edit(
            "You are missing the following rights to use this command: CanPromoteUsers."
        )
        return False
    return True


async def can_change_info(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.reply("Only admins can execute this command!")
        return False
    if not perm.change_info:
        await event.reply(
            "You are missing the following rights to use this command: CanChangeInfo."
        )
        return False
    return True


async def can_pin_messages(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.reply("Only admins can execute this command!")
        return False
    if not perm.pin_messages:
        await event.reply(
            "You are missing the following rights to use this command: CanPinMessages."
        )
        return False
    return True


async def can_ban_users(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.reply("Only admins can execute this command!")
        return False
    if not perm.ban_users:
        await event.reply(
            "You are missing the following rights to use this command: CanBanUsers."
        )
        return False
    return True


async def is_owner(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.reply("Only admins can execute this command!")
        return False
    if not perm.is_creator:
        await event.reply("You need to be the chat Creator to do this!")
        return False
    return True


async def check_owner(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_creator:
        return False
    return True


async def can_del_msg(event, user_id):
    perm = await tbot.get_permissions(event.chat_id, user_id)
    if not perm.is_admin:
        await event.reply("You need to be an admin to do this.")
        return False
    if not perm.delete_messages:
        await event.reply(
            "You are missing the following rights to use this command: CanDeleteMessages."
        )
        return False
    return True


async def is_admin(chat_id, user):
    try:
        perm = await tbot.get_permissions(chat_id, user)
    except UserNotParticipantError:
        return False
    if not perm.is_admin:
        return False
    return True


async def get_user(event):
    args = event.pattern_match.group(1).split(" ", 1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await tbot.get_entity(previous_message.sender_id)
        extra = event.pattern_match.group(1)
    elif args:
        extra = None
        user = args[0]
        if len(args) == 2:
            extra = args[1]
        if user.isnumeric():
            user = int(user)
        if not user:
            await event.reply(
                "I don't know who you're talking about, you're going to need to specify a user...!"
            )
            return
        try:
            user_obj = await tbot.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.reply(str(err))
            return

    return user_obj, extra


async def extract_time(message, time_val):
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await message.reply("Invalid time amount specified.")
            return ""
        if unit == "m":
            bantime = int(time_num) * 60
        elif unit == "h":
            bantime = int(time_num) * 60 * 60
        elif unit == "d":
            bantime = int(time_num) * 24 * 60 * 60
        else:
            return
        return bantime
    else:
        await message.reply(
            "Invalid time type specified. Expected m,h, or d, got: {}".format(
                time_val[-1]
            )
        )
        return False


def g_time(time):
    time = int(time)
    if time >= 86400:
        time = time / (60 * 60 * 24)
        text = f"{int(time)} days"
        if not time - int(time) == 0:
            kuk = (time - int(time)) * 24
            text += f" {int(kuk)} hours"
    elif time >= 3600 < 86400:
        time = time / (60 * 60)
        text = f"{int(time)} hours"
        if not time - int(time) == 0:
            kuk = (time - int(time)) * 60
            text += f" {int(kuk)} minutes"
    elif time >= 60 < 3600:
        time = time / 60
        text = f"{int(time)} minutes"
        if not time - int(time) == 0:
            kuk = (time - int(time)) * 60
            text += f" {int(kuk)} seconds"
    return text


BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((btnurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)


def button_parser(text):
    if "buttonalert" in text:
        text = text.replace("\n", "\\n").replace("\t", "\\t")
    buttons = []
    note_data = ""
    prev = 0
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev : match.start(1)]
            prev = match.end(1)
            if bool(match.group(5)) and buttons:
                buttons[-1].append(
                    Button.url(match.group(2), match.group(4).replace(" ", ""))
                )
            else:
                buttons.append(
                    [Button.url(match.group(2), match.group(4).replace(" ", ""))]
                )

        # if odd, escaped -> move along
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]
    if str(buttons) == "[]":
        buttons = None
    try:
        return note_data, buttons
    except:
        return note_data


BUTTONS = {}


def get_reply_msg_btns_text(message):
    text = ""
    for column in message.reply_markup.rows:
        btn_num = 0
        for btn in column.buttons:
            btn_num += 1
            btn.text
            if btn.url:
                btn.url
                text += f"\n[{btn.text}](btnurl:{btn.url}*!repl!*)"
                if btn_num > 1:
                    text = text.replace("*!repl!*", ":same")
                else:
                    text = text.replace("*!repl!*", "")
    return text


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


def gen_math_question():
    no1 = randint(1, 100)
    no2 = randint(10, 100)
    k = [1, 2, 3]
    op = choice(k)
    if op == 1:
        x = f"{no1}+{no2}=?"
        ans = no1 + no2
    elif op == 2:
        if no1 > no2:
            x = f"{no1}-{no2}=?"
            ans = no1 - no2
        else:
            x = f"{no2}-{no1}=?"
            ans = no2 - no1
    elif op == 3:
        kek = [1, 2]
        kek = choice(kek)
        if kek == 1:
            x = f"{no1}x{no2}=?"
            ans = no1 * no2
        elif kek == 2:
            if no1 > no2:
                x = f"{no1}÷{no2}=?"
                ans = no1 // no2
            else:
                x = f"{no2}÷{no1}=?"
                ans = no2 // no1
    return x, ans


def rand_no():
    a = randint(0, 1000)
    b = randint(0, 1000)
    c = randint(0, 1000)
    d = randint(0, 1000)
    f = randint(0, 1000)
    e = randint(0, 1000)
    g = randint(0, 1000)
    h = randint(0, 1000)
    return a, b, c, d, e, f, g, h


def generate_image(text, font_sizes=[195, 181, 210]):
    image_captcha = ImageCaptcha(width=1080, height=720, font_sizes=font_sizes)
    path = "./captcha.png"
    image_captcha.write(text, path)
    return path


def math_captcha_pic(text):
    fonts = (
        ImageFont.truetype("./Evelyn/modules/sql/Merriweather-Bold.ttf", 75),
        ImageFont.truetype("./Evelyn/modules/sql/DroidSans.ttf", 75),
        ImageFont.truetype("./Evelyn/modules/sql/Algerian Regular.ttf", 75),
    )
    img = Image.new("RGB", (430, 125), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    image_widthz, image_heightz = img.size
    w, h = draw.textsize(text, font=choice(fonts))
    draw.text(
        ((image_widthz - w) / 2, (image_heightz - h) / 2),
        text[:2],
        font=choice(fonts),
        fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
    )
    draw.text(
        (
            (image_widthz - w + 150) / 2,
            (image_heightz - h - 3) / 2,
        ),
        text[:3][2:],
        font=choice(fonts),
        fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
    )
    draw.text(
        (
            (image_widthz - w + 260) / 2,
            (image_heightz - h - 3) / 2,
        ),
        text[:5][3:],
        font=choice(fonts),
        fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
    )
    draw.text(
        (
            (image_widthz - w + randint(400, 420)) / 2,
            (image_heightz - h - 3) / 2,
        ),
        text[:6][5:],
        font=choice(fonts),
        fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
    )
    draw.text(
        (
            (image_widthz - w + randint(500, 550)) / 2,
            (image_heightz - h - 3) / 2,
        ),
        text[:7][6:],
        font=choice(fonts),
        fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
    )
    w, h = img.size
    for i in range(150):
        x1 = randint(0, w)
        y1 = randint(0, h)
        draw.line(
            ((x1, y1), (x1 - 1, y1 - 1)),
            fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
            width=5,
        )
    for i in range(8):
        x1 = randint(0, w)
        y1 = randint(0, h)
        draw.line(
            ((x1, y1), (x1 - 1, y1 - 1)),
            fill=(randint(0, 255), randint(0, 255), randint(0, 255)),
            width=1000,
        )
    img.save("final.png", "png")
    return "final.png"


# soon
def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


async def format_fill(event, text):
    first_name = event.sender.first_name
    last_name = event.sender.last_name
    if last_name:
        full_name = first_name + last_name
    else:
        full_name = first_name
    user_id = event.sender_id
    title = event.chat.title
    chat_id = event.chat_id
    chat_username = event.chat.username
    username = event.sender.username
    mention = f'<a href="tg://user?id={user_id}">{first_name}</a>'
    text = text.format(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        user_id=user_id,
        title=title,
        chat_id=chat_id,
        chat_username=chat_username,
        username=username,
        mention=mention,
    )
    return text
