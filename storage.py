import json
import os


def load_users():

    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_users(data):

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_memory():

    if os.path.exists("memory.json"):
        with open("memory.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_memory(data):

    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)