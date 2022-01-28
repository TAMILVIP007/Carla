from .. import db

chats = db.chats


def add_chat(chat_id: int):
    c = _chats["chats"] if (_chats := chats.find_one({"type": "main"})) else []
    c.append(chat_id)
    chats.update_one({"type": "main"}, {"$set": {"chats": c}}, upsert=True)


def rm_chat(chat_id: int):
    c = _chats["chats"] if (_chats := chats.find_one({"type": "main"})) else []
    if chat_id in c:
        c.remove(chat_id)
    chats.update_one({"type": "main"}, {"$set": {"chats": c}}, upsert=True)


def get_all_chat_id():
    if _chats := chats.find_one({"type": "main"}):
        return _chats["chats"]
    return None


def is_chat(chat_id: int):
    _chats = chats.find_one({"type": "main"})
    return bool(_chats and chat_id in _chats["chats"])
