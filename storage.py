import json
import os


# ==========================
# ユーザー情報
# ==========================

def load_users():

    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_users(data):

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================
# 相談履歴
# ==========================

def load_memory():

    if os.path.exists("memory.json"):
        with open("memory.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_memory(data):

    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================
# 利用ログ
# ==========================

def load_logs():

    if os.path.exists("logs.json"):
        with open("logs.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_logs(data):

    with open("logs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_log(category):

    logs = load_logs()

    logs[category] = logs.get(category, 0) + 1

    save_logs(logs)