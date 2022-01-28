from .. import db

feds = db.feds
fbans = db.fbans
fsubs = db.fsubs
fadmins = db.fadmins


def new_fed(owner_id: int, fed_id, fedname):
    feds.update_one(
        {"owner_id": owner_id},
        {
            "$set": {
                "fed_id": fed_id,
                "fedname": fedname,
                "fedadmins": [],
                "flog": None,
                "chats": [],
                "report": True,
            }
        },
        upsert=True,
    )


def del_fed(fed_id):
    feds.delete_one({"fed_id": fed_id})
    fbans.delete_one({"fed_id": fed_id})
    fsubs.delete_one({"fed_id": fed_id})


def transfer_fed(owner_id: int, user_id: int):
    if _fed := feds.find_one({"owner_id": owner_id}):
        feds.update_one(
            {"fed_id": _fed["fed_id"]}, {"$set": {"owner_id": user_id}}, upsert=True
        )


def rename_fed(fed_id, fname):
    if _fed := feds.find_one({"fed_id": fed_id}):
        feds.update_one({"fed_id": fed_id}, {"$set": {"fedname": fname}}, upsert=True)


def chat_join_fed(fed_id, chat_id: int):
    if _fed := feds.find_one({"fed_id": fed_id}):
        chats = _fed["chats"]
        chats.append(chat_id)
        feds.update_one({"fed_id": fed_id}, {"$set": {"chats": chats}}, upsert=True)


def user_demote_fed(fed_id, user_id: int):
    if _fed := feds.find_one({"fed_id": fed_id}):
        fedadmins = _fed["fedadmins"]
        fedadmins.remove(user_id)
        feds.update_one(
            {"fed_id": fed_id}, {"$set": {"fedadmins": fedadmins}}, upsert=True
        )


def user_join_fed(fed_id, user_id: int):
    if _fed := feds.find_one({"fed_id": fed_id}):
        fedadmins = _fed["fedadmins"]
        fedadmins.append(user_id)
        feds.update_one(
            {"fed_id": fed_id}, {"$set": {"fedadmins": fedadmins}}, upsert=True
        )


def chat_leave_fed(fed_id, chat_id):
    if _fed := feds.find_one({"fed_id": fed_id}):
        chats = _fed["chats"]
        chats.remove(chat_id)
        feds.update_one({"fed_id": fed_id}, {"$set": {"chats": chats}}, upsert=True)


def fban_user(fed_id, user_id: str, firstname, lastname, reason, time: str):
    f_bans = (
        _fban["fbans"] if (_fban := fbans.find_one({"fed_id": fed_id})) else {}
    )

    f_bans[str(user_id)] = [firstname, lastname, reason, time]
    fbans.update_one({"fed_id": fed_id}, {"$set": {"fbans": f_bans}}, upsert=True)


def unfban_user(fed_id, user_id):
    f_bans = (
        _fban["fbans"] if (_fban := fbans.find_one({"fed_id": fed_id})) else {}
    )

    if f_bans[str(user_id)]:
        del f_bans[str(user_id)]
    fbans.update_one({"fed_id": fed_id}, {"$set": {"fbans": f_bans}}, upsert=True)


def super_fban(user_id):
    print("soon")


def get_user_owner_fed_full(owner_id):
    if _all_feds := feds.find_one({"owner_id": owner_id}):
        return _all_feds["fed_id"], _all_feds["fedname"]
    return None


def search_fed_by_id(fed_id):
    return _x_fed if (_x_fed := feds.find_one({"fed_id": fed_id})) else None


def get_len_fbans(fed_id):
    if _x_fbans := fbans.find_one({"fed_id": fed_id}):
        return len(_x_fbans.get("fbans"))
    return 0


def get_all_fbans(fed_id):
    if _x_fbans := fbans.find_one({"fed_id": fed_id}):
        return _x_fbans.get("fbans")
    return None


def get_chat_fed(chat_id):
    _x = feds.find({})
    for x in _x:
        if chat_id in x["chats"]:
            return_able = x["fed_id"]
            if len(return_able) == 0:
                return None
            return return_able
    return None


def get_fban_user(fed_id, user_id: str):
    if _x_data := fbans.find_one({"fed_id": fed_id}):
        if _xx_data := _x_data.get("fbans"):
            if __xxx_data := _xx_data.get(str(user_id)):
                return True, __xxx_data[2], __xxx_data[3]
    return False, None, None


def search_user_in_fed(fed_id, user_id: int):
    if _x := feds.find_one({"fed_id": fed_id}):
        _admins = _x.get("fedadmins")
        if _admins and len(_admins) > 0 and user_id in _admins:
            return True
    return False


def user_feds_report(user_id: int):
    return _x["report"] if (_x := feds.find_one({"owner_id": user_id})) else True


def set_feds_setting(user_id: int, mode):
    feds.update_one({"owner_id": user_id}, {"$set": {"report": mode}}, upsert=True)


def get_all_fed_admins(fed_id):
    _fed = feds.find_one({"fed_id": fed_id})
    x_admins = _fed["fedadmins"]
    x_owner = _fed["owner_id"]
    x_admins.append(x_owner)
    return x_admins


def get_fed_log(fed_id):
    return _fed["flog"] if (_fed := feds.find_one({"fed_id": fed_id})) else False


def get_all_fed_chats(fed_id):
    _fed = feds.find_one({"fed_id": fed_id})
    return _fed.get("chats")


def sub_fed(fed_id: str, my_fed: str):
    if x_mysubs := fsubs.find_one({"fed_id": my_fed}):
        my_subs = x_mysubs["my_subs"]
    else:
        my_subs = []
    my_subs.append(fed_id)
    my_subs = list(set(my_subs))
    fsubs.update_one({"fed_id": my_fed}, {"$set": {"my_subs": my_subs}}, upsert=True)
    if x_fedsubs := fsubs.find_one({"fed_id": fed_id}):
        fed_subs = x_fedsubs["fed_subs"]
    else:
        fed_subs = []
    fed_subs.append(my_fed)
    fed_subs = list(set(fed_subs))
    fsubs.update_one({"fed_id": fed_id}, {"$set": {"fed_subs": fed_subs}}, upsert=True)


def unsub_fed(fed_id: str, my_fed: str):
    if x_mysubs := fsubs.find_one({"fed_id": my_fed}):
        my_subs = x_mysubs["my_subs"]
    else:
        my_subs = []
    if fed_id in my_subs:
        my_subs.remove(fed_id)
    fsubs.update_one({"fed_id": my_fed}, {"$set": {"my_subs": my_subs}}, upsert=True)
    if x_fedsubs := fsubs.find_one({"fed_id": fed_id}):
        fed_subs = x_fedsubs["fed_subs"]
    else:
        fed_subs = []
    if my_fed in fed_subs:
        fed_subs.remove(my_fed)
    fsubs.update_one({"fed_id": fed_id}, {"$set": {"fed_subs": fed_subs}}, upsert=True)


def get_my_subs(fed_id):
    if x_mysubs := fsubs.find_one({"fed_id": fed_id}):
        return x_mysubs.get("my_subs") or []
    return []


def get_fed_subs(fed_id):
    if x_fedsubs := fsubs.find_one({"fed_id": fed_id}):
        return x_fedsubs.get("fed_subs") or []
    return []


def add_fname(user_id, fname):
    fadmins.update_one({"user_id": user_id}, {"$set": {"fname": fname}}, upsert=True)


def get_fname(user_id):
    return x["fname"] if (x := fadmins.find_one({"user_id": user_id})) else None


def set_fed_log(fed_id: str, chat_id=None):
    feds.update_one({"fed_id": fed_id}, {"$set": {"flog": chat_id}}, upsert=True)


def get_all_fed_admin_feds(user_id):
    fed = {}
    admin = [x.get("fed_id") for x in feds.find() if user_id in x.get("fedadmins")]
    if owner := feds.find_one({"owner_id": user_id}):
        fed["owner"] = owner["fed_id"]
    if admin:
        fed["admin"] = admin
    return fed
