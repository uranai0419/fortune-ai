from flask import Flask, request
import requests
import google.generativeai as genai

from config import ACCESS_TOKEN, GEMINI_API_KEY, MODEL_NAME
from prompts import *
from tarot import draw_tarot
from storage import *

app = Flask(__name__)

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(MODEL_NAME)

# ユーザー状態
user_states = {}


@app.route("/")
def home():
    return "Fortune AI Running"


@app.route("/callback", methods=["POST"])
def callback():

    print("★★★★ callback called ★★★★")

    body = request.json

    print(body)

    events = body.get("events", [])

    for event in events:

        if event["type"] != "message":
            continue

        user_text = event["message"]["text"]
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        reply_text = ""

        # 続き相談
        if user_text in ["続き", "前回の続き", "続きを占って"]:

            memory = load_memory()
            users = load_users()

            old_text = memory.get(user_id, "")

            if old_text == "":
                reply_text = "過去の相談履歴がありません✨"

            else:
                prompt = f"""
   過去の相談履歴

   {old_text}

   前回からの流れを考慮して、
   現在の状況を優しく具体的に鑑定してください。
   """

                try:
                    response = model.generate_content(prompt)
                    reply_text = response.text

                except Exception:
                    reply_text = "現在鑑定できません。"

        # Zoom鑑定
        elif "Zoom" in user_text or "zoom" in user_text:

            reply_text = """
🌙Zoom鑑定をご希望いただきありがとうございます✨

AI鑑定では読み切れない

・相手の本音
・復縁の可能性
・結婚のタイミング
・本当に動くべき時期

などを、

実際の占い師が
あなたのお話を伺いながら
丁寧に鑑定いたします✨

▼ご予約はこちら

https://forms.gle/iovCGpzebfGPzH9H9

ご予約をお待ちしております🌸
"""
        # 恋愛運
        elif user_text in ["💕恋愛運", "恋愛", "恋愛運"]:

            user_states[user_id] = "love"

            reply_text = (
                "💕恋愛運鑑定\n\n"
                "お名前を入力してください✨"
            )

        # 仕事運
        elif user_text in ["💼仕事運", "仕事", "仕事運"]:

            user_states[user_id] = "work"

            reply_text = (
                "💼仕事運鑑定\n\n"
                "お名前を入力してください✨"
            )

        # 金運
        elif user_text in ["💰金運", "金運"]:

            user_states[user_id] = "money"

            reply_text = (
                "💰金運鑑定\n\n"
                "お名前を入力してください✨"
            )

        # 相性占い
        elif user_text in ["🔮相性占い", "相性", "相性占い"]:

            user_states[user_id] = "compatibility"

            reply_text = (
                "🔮相性占い\n\n"
                "あなたのお名前を入力してください✨"
            )

        # 今日の運勢
        elif user_text in ["☀本日の運勢", "本日の運勢", "運勢"]:

        try:

            response = model.generate_content(DAILY_PROMPT)

            reply_text = response.text

            except Exception as e:
                print(e)
                reply_text = "現在、本日の運勢を鑑定できません。"

        # 生年月日入力
        elif user_states.get(user_id) == "birthday":

            users = load_users()

            users[user_id]["birthday"] = user_text

            save_users(users)

            user_states[user_id] = "consultation"

            reply_text = (
                "相談内容を入力してください✨\n\n"
                "例：好きな人との今後を占ってください"
            )

        # 相談内容入力
        elif user_states.get(user_id) == "consultation":

            users = load_users()

            category = users[user_id]["type"]

            if category == "love":
                base_prompt = LOVE_PROMPT

            elif category == "work":
                base_prompt = WORK_PROMPT

            elif category == "money":
                base_prompt = MONEY_PROMPT

            elif category == "total":
                base_prompt = TOTAL_PROMPT

            else:
                base_prompt = LIFE_PROMPT

            memory = load_memory()

            old_text = memory.get(user_id, "")

            prompt = f"""

前回の相談：
あなたは優秀な占い師です。

同じ相談者との会話が続いています。

【過去の相談履歴】
{old_text}

【名前】
{users[user_id]['name']}

【生年月日】
{users[user_id]['birthday']}

{base_prompt}

今回の相談内容

{user_text}

過去の相談内容も考慮して、
前回とのつながりを意識しながら、
優しく具体的に鑑定してください。

"""

            try:

                response = model.generate_content(prompt)

                reply_text = response.text + """

🌙今回の鑑定から見える流れをお伝えしました✨

ご縁や人の気持ちは日々変化していくため、
AIによる鑑定だけでは読み切れない部分もあります。

もし、

・相手の本音をもっと深く知りたい
・復縁の可能性を詳しく見てほしい
・いつ動くべきか知りたい
・自分に合った開運方法を知りたい

という場合は、

✨実際の占い師によるZoom鑑定✨

で、お話を伺いながら丁寧に鑑定することもできます🌙

ご希望の方は

「Zoom鑑定希望」

と送ってください🌸

"""


            except Exception as e:

                print(e)

                reply_text = "現在鑑定できません。"

            memory[user_id] = old_text + "\n" + user_text

            save_memory(memory)

            user_states.pop(user_id, None)
        # 相性占い：あなたの名前
        elif user_states.get(user_id) == "compatibility":

            users = load_users()

            users[user_id] = {
                "my_name": user_text
            }

            save_users(users)

            user_states[user_id] = "compatibility_birthday"

            reply_text = (
                "あなたの生年月日を入力してください✨\n\n"
                "例：1984/04/19"
            )

        # あなたの生年月日
        elif user_states.get(user_id) == "compatibility_birthday":

            users = load_users()

            users[user_id]["my_birthday"] = user_text

            save_users(users)

            user_states[user_id] = "partner_name"

            reply_text = (
                "お相手のお名前を入力してください✨"
            )

        # 相手の名前
        elif user_states.get(user_id) == "partner_name":

            users = load_users()

            users[user_id]["partner_name"] = user_text

            save_users(users)

            user_states[user_id] = "partner_birthday"

            reply_text = (
                "お相手の生年月日を入力してください✨\n\n"
                "分からない場合は「不明」でも大丈夫です。"
            )

        # 相手の生年月日
        elif user_states.get(user_id) == "partner_birthday":

            users = load_users()

            users[user_id]["partner_birthday"] = user_text

            save_users(users)

            prompt = f"""

{COMPATIBILITY_PROMPT}

【あなた】
名前：
{users[user_id]['my_name']}

生年月日：
{users[user_id]['my_birthday']}

【お相手】
名前：
{users[user_id]['partner_name']}

生年月日：
{users[user_id]['partner_birthday']}

"""

            try:

                response = model.generate_content(prompt)

                reply_text = response.text + """
🌙今回の鑑定から見える流れをお伝えしました✨

ご縁や人の気持ちは日々変化していくため、
AIによる鑑定だけでは読み切れない部分もあります。

もし、

・相手の本音をもっと深く知りたい
・復縁の可能性を詳しく見てほしい
・いつ動くべきか知りたい
・自分に合った開運方法を知りたい

という場合は、

実際の占い師によるZoom鑑定で、
お話を伺いながら丁寧に鑑定することもできます✨

ご希望の方は

「Zoom鑑定希望」

と送ってください🌸
"""


            except Exception as e:

                print(e)

                reply_text = "現在、相性占いを行えません。"

            user_states.pop(user_id, None)
        # その他
        else:

            reply_text = (
                "🌙運命鑑定へようこそ🌙\n\n"
                "💕恋愛運\n"
                "💼仕事運\n"
                "💰金運\n"
                "☀本日の運勢\n"
                "🔮相性占い\n"
                "🌙Zoom鑑定\n\n"
                "ご希望のメニューを送信してください✨"
            )

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": reply_text[:5000]
                }
            ]
        }

        response_line = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=data
        )

        print(response_line.status_code)
        print(response_line.text)

    return "OK"


if __name__ == "__main__":
    app.run(debug=True)