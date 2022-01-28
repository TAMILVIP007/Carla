from .. import db

rules = db.rules


def set_rules(chat_id: int, rule_s: str):
    rules.update_one(
        {"chat_id": chat_id},
        {"$set": {"rules": rule_s, "private": False, "button": "Rules"}},
        upsert=True,
    )


def get_rules(chat_id: int):
    if _rules := rules.find_one({"chat_id": chat_id}):
        return _rules["rules"]
    return False


def del_rules(chat_id: int):
    if _rules := rules.find_one({"chat_id": chat_id}):
        rules.delete_one({"chat_id": chat_id})


def set_private_rules(chat_id: int, mode):
    if _rules := rules.find_one({"chat_id": chat_id}):
        rule_s = _rules["rules"]
        button = _rules["button"]
    else:
        rule_s = ""
        button = "Rules"
    rules.update_one(
        {"chat_id": chat_id},
        {"$set": {"rules": rule_s, "private": mode, "button": button}},
        upsert=True,
    )


def get_private_rules(chat_id: int):
    if _rules := rules.find_one({"chat_id": chat_id}):
        return _rules["private"]
    return False


def set_rules_button(chat_id, button):
    if _rules := rules.find_one({"chat_id": chat_id}):
        rule_s = _rules["rules"]
        p = _rules["private"]
    else:
        rule_s = ""
        p = False
    rules.update_one(
        {"chat_id": chat_id},
        {"$set": {"rules": rule_s, "private": p, "button": button}},
        upsert=True,
    )


def get_rules_button(chat_id: int):
    if _rules := rules.find_one({"chat_id": chat_id}):
        return _rules["button"]
    return "Rules"
