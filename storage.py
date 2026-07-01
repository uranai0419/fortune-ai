import json
import os
from datetime import datetime

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

    # 今日の日付
    today = datetime.now().strftime("%Y-%m-%d")

    # 累計
    logs[category] = logs.get(category, 0) + 1

    # 今日の利用回数
    logs.setdefault("today", {})
    logs["today"].setdefault(today, {})
    logs["today"][today][category] = (
        logs["today"][today].get(category, 0) + 1
    )

    save_logs(logs)

def add_today_user(user_id):

    logs = load_logs()

    today = datetime.now().strftime("%Y-%m-%d")

    logs.setdefault("users", {})
    logs["users"].setdefault(today, [])

    if user_id not in logs["users"][today]:
        logs["users"][today].append(user_id)

    save_logs(logs)

def is_repeat_user(user_id):

    users = load_users()

    return user_id in users