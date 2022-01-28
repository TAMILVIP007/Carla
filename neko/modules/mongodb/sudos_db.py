from neko.modules import db

sudo_m = db.sudo


def add_sudo(user_id: int, name: str):
    sudos = sudo_m.find_one({"type": "staffs"})
    if sudos:
        try:
            sudos = sudos["sudo"]
        except:
            sudos = {}
    else:
        sudos = {}
    sudos[user_id] = name
    sudo_m.update_one({"type": "staffs"}, {"$set": {"sudo": sudos}}, upsert=True)


def add_dev(user_id: int, name: str):
    devs = sudo_m.find_one({"type": "staffs"})
    if devs:
        try:
            devs = devs["dev"]
        except:
            devs = {}
    else:
        devs = {}
    devs[user_id] = name
    sudo_m.update_one({"type": "staffs"}, {"$set": {"dev": devs}}, upsert=True)


def rem_sudo(user_id: int):
    sudo = sudo_m.find_one({"type": "staffs"})
    if not sudo:
        return False
    try:
        sudo = sudo["sudo"]
    except:
        sudo = {}
    del sudo[user_id]
    sudo_m.update_one({"type": "staffs"}, {"$set": {"sudo": sudo}}, upsert=True)


def rem_dev(user_id: int):
    dev = sudo_m.find_one({"type": "staffs"})
    if not dev:
        return False
    try:
        dev = dev["dev"]
    except:
        dev = {}
    del dev[user_id]
    sudo_m.update_one({"type": "staffs"}, {"$set": {"dev": dev}}, upsert=True)


def get_sudos():
    if sudo := sudo_m.find_one({"type": "staffs"}):
        try:
            return sudo["sudo"]
        except:
            return []
    return None


def get_devs():
    if dev := sudo_m.find_one({"type": "staffs"}):
        try:
            return dev["dev"]
        except:
            return []
    return None
