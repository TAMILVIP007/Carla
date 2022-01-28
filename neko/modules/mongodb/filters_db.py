from neko.modules import db

filters = db.filters


def save_filter(chat_id, name, reply, id=None, hash=None, reference=None, type=None):
    name = name.lower().strip()
    if _filter := filters.find_one({"chat_id": chat_id}):
        _filters = _filter["filters"]
        if _filters is None:
            _filters = {}
    else:
        _filters = {}
    _filters[name] = {
        "reply": reply,
        "id": id,
        "hash": hash,
        "ref": reference,
        "mtype": type,
    }
    filters.update_one(
        {"chat_id": chat_id}, {"$set": {"filters": _filters}}, upsert=True
    )


def delete_filter(chat_id, name):
    name = name.strip().lower()
    _filters = filters.find_one({"chat_id": chat_id})
    _filter = {} if not _filters else _filters["filters"]
    if name in _filter:
        del _filter[name]
        filters.update_one(
            {"chat_id": chat_id}, {"$set": {"filters": _filter}}, upsert=True
        )


def get_filter(chat_id, name):
    name = name.strip().lower()
    _filters = filters.find_one({"chat_id": chat_id})
    _filter = {} if not _filters else _filters["filters"]
    if name in _filter:
        return _filter[name]
    return False


def get_all_filters(chat_id):
    if _filters := filters.find_one({"chat_id": chat_id}):
        return _filters["filters"]
    return None


def delete_all_filters(chat_id):
    if _filters := filters.find_one({"chat_id": chat_id}):
        filters.delete_one({"chat_id": chat_id})
        return True
    return False
