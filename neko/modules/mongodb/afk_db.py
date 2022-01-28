import time

from .. import db

afk = db.afk


def set_afk(user_id: int, first_name="User", reason=None):
    afk.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "first_name": first_name,
                "reason": reason,
                "time": time.time(),
            }
        },
        upsert=True,
    )


def unset_afk(user_id):
    if _afk := afk.find_one({"user_id": user_id}):
        afk.delete_one({"user_id": user_id})


def is_afk(user_id):
    return bool(_afk := afk.find_one({"user_id": user_id}))


def get_afk(user_id):
    return _afk if (_afk := afk.find_one({"user_id": user_id})) else False
