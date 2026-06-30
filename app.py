from flask import Flask, request
import requests
import google.generativeai as genai

from config import ACCESS_TOKEN, GEMINI_API_KEY, MODEL_NAME
from prompts import *
from tarot import draw_tarot
from storage import *

ADMIN_USER_ID = "U78cd818495a8e092c9f2dc6b2761b5e6"

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

        print("===== USER ID =====")
        print(user_id)
        print("===================")

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
        elif "zoom" in user_text.lower():
            
            add_log("zoom_menu")

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

            add_log("love")

            user_states[user_id] = "love"
            
            reply_text = (
                "💕恋愛運鑑定\n\n"
                "お名前を入力してください✨"
            )

        # 仕事運
        elif user_text in ["💼仕事運", "仕事", "仕事運"]:

            user_states[user_id] = "work"

            add_log("work")

            reply_text = (
                "💼仕事運鑑定\n\n"
                "お名前を入力してください✨"
            )

        # 金運
        elif user_text in ["💰金運", "金運"]:

            user_states[user_id] = "money"

            add_log("money")

            reply_text = (
                "💰金運鑑定\n\n"
                "お名前を入力してください✨"
            )

        # 運命鑑定
        elif user_text in ["🔮運命鑑定", "運命鑑定", "運命", "生年月日鑑定"]:

            user_states[user_id] = "destiny"

            add_log("destiny")

            reply_text = (
                "🔮AI運命ちゃん\n\n"
                "お名前を入力してください✨"
            )
        
        # 今日の運勢
        elif user_text in ["☀今日の運勢", "今日の運勢", "運勢"]:

            add_log("daily")

            try:

                response = model.generate_content(DAILY_PROMPT)
                reply_text = response.text

            except Exception as e:
                print(e)
                reply_text = "現在、本日の運勢を鑑定できません。"

        # 名前入力（恋愛・仕事・金運共通）
        elif user_states.get(user_id) in ["love", "work", "money"]:

            users = load_users()

            users[user_id] = {
                "name": user_text,
                "type": user_states[user_id]
            }

            save_users(users)

            user_states[user_id] = "birthday"

            reply_text = (
                "生年月日を入力してください✨\n\n"
                "例：1990/01/01"
            )


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

            else:
                reply_text = (
                    "エラーが発生しました。\n"
                    "もう一度メニューから選択してください。"
                )
                user_states.pop(user_id, None)
                base_prompt = None

            if base_prompt:

                memory = load_memory()
                old_text = memory.get(user_id, "")

                prompt = f"""
            あなたは優秀な占い師です。

　　　　　　（過去の相談履歴）
　　　　　　{old_text}

　　　　　　【名前】
　　　　　　{users[user_id]['name']}

　　　　　　【生年月日】
　　　　　　{users[user_id]['birthday']}

　　　　　　{base_prompt}

　　　　　　【今回の相談内容】
　　　　　　{user_text}

　　　　　　過去の相談内容も考慮し、
　　　　　　前回とのつながりを意識しながら、
　　　　　　相談者だけに寄り添う具体的な鑑定をしてください。
　　　　　　"""

                try:

                    response = model.generate_content(prompt)

                    reply_text = response.text + """

🌙今回の鑑定から見える流れをお伝えしました✨

ご縁や状況は日々変化していくため、
AIだけでは読み切れない部分もあります。

もっと深く知りたい方は

🌙Zoom鑑定希望

と送ってください✨
"""

                except Exception as e:

                    print(e)

                    reply_text = "現在鑑定できません。"

                memory[user_id] = (
                    old_text
                    + "\n【相談】"
                    + user_text
                    + "\n【鑑定】"
                    + reply_text
                )

                save_memory(memory)

                user_states.pop(user_id, None)


        # 運命鑑定：名前
        elif user_states.get(user_id) == "destiny":

            users = load_users()

            users.setdefault(user_id, {})
            users[user_id]["name"] = user_text

            save_users(users)

            user_states[user_id] = "destiny_birthday"

            reply_text = (
                "生年月日を入力してください✨\n\n"
                "例：1990/01/01"
            )

        # 運命鑑定：生年月日
        elif user_states.get(user_id) == "destiny_birthday":

            users = load_users()

            users[user_id]["birthday"] = user_text

            save_users(users)

            user_states[user_id] = "destiny_consultation"

            reply_text = (
                "相談内容を入力してください✨\n\n"
                "例：私の人生の流れを見てください"
            )
        
        # 運命鑑定：相談内容
        elif user_states.get(user_id) == "destiny_consultation":

            users = load_users()

            memory = load_memory()
            old_text = memory.get(user_id, "")

            prompt = f"""
        【過去の相談履歴】
        {old_text}

        【名前】
        {users[user_id]['name']}

        【生年月日】
        {users[user_id]['birthday']}

        {DESTINY_PROMPT}

        【今回の相談】
        {user_text}

        過去の相談内容も考慮しながら、
        相談者の本質・運命・人生の流れを読み解き、
        具体的で温かい鑑定をしてください。
        """

            try:

                response = model.generate_content(prompt)

                reply_text = response.text

            except Exception as e:

                print(e)

                reply_text = "現在、運命鑑定を行えません。"

            memory[user_id] = (
                old_text
                + "\n【相談】"
                + user_text
                + "\n【鑑定】"
                + reply_text
            )

            save_memory(memory)

            user_states.pop(user_id, None)

        # 管理者レポート
        elif user_text == "レポート" and user_id == ADMIN_USER_ID:

            logs = load_logs()

            today = datetime.now().strftime("%Y-%m-%d")

            today_logs = logs.get("today", {}).get(today, {})

            today_users = len(logs.get("users", {}).get(today, []))

            reply_text = (
                "📊 AI占い館レポート\n\n"

                f"👥 今日の利用人数：{today_users}人\n\n"

                "【今日の利用回数】\n"
                f"💕恋愛ちゃん：{today_logs.get('love',0)}回\n"
                f"💼仕事ちゃん：{today_logs.get('work',0)}回\n"
                f"💰金運ちゃん：{today_logs.get('money',0)}回\n"
                f"🔮運命ちゃん：{today_logs.get('destiny',0)}回\n"
                f"☀運勢ちゃん：{today_logs.get('daily',0)}回\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "🌙Zoom分析（今日）\n"

                f"メニュー表示：{today_logs.get('zoom_menu',0)}回\n"
                f"Zoom希望：{today_logs.get('zoom_request',0)}回\n"
                f"予約完了：{today_logs.get('zoom_booked',0)}件\n\n"

                "────────────\n\n"

                "────────────\n\n"

                "【累計利用回数】\n"
                f"💕恋愛ちゃん：{logs.get('love',0)}回\n"
                f"💼仕事ちゃん：{logs.get('work',0)}回\n"
                f"💰金運ちゃん：{logs.get('money',0)}回\n"
                f"🔮運命ちゃん：{logs.get('destiny',0)}回\n"
                f"☀運勢ちゃん：{logs.get('daily',0)}回\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "🌙Zoom分析（累計）\n"

                f"メニュー表示：{logs.get('zoom_menu',0)}回\n"
                f"Zoom希望：{logs.get('zoom_request',0)}回\n"
                f"予約完了：{logs.get('zoom_booked',0)}件"
            )


        # Zoom鑑定希望
        elif user_text in ["Zoom鑑定希望", "zoom鑑定希望"]:

            add_log("zoom_request")

            reply_text = (
                "ありがとうございます✨\n\n"
                "Zoom鑑定のご希望を承りました。\n\n"
                "担当者より日程調整のご連絡をいたしますので、"
                "少々お待ちください🌸"
            )

        # Zoom予約完了（管理者専用）
        elif (
            user_text == "予約完了"
            and user_id == ADMIN_USER_ID
        ):

            add_log("zoom_booked")

            reply_text = (
                "✅ Zoom予約件数を1件追加しました。"
            )

        # その他
        else:

            reply_text = (
                "🌙AI占い館へようこそ🌙\n\n"
                "💕AI恋愛ちゃん\n"
                "💼AI仕事ちゃん\n"
                "💰AI金運ちゃん\n"
                "🔮AI運命ちゃん\n"
                "☀AI運勢ちゃん\n"
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


@app.route("/notify", methods=["POST"])
def notify():

    print("===== /notify called =====")

    data = request.json
    print(data)

    message = data["message"]

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "to": ADMIN_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message[:5000]
            }
        ]
    }

    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=body
    )

    print("===== LINE PUSH RESULT =====")
    print(r.status_code)
    print(r.text)

    return "OK"

if __name__ == "__main__":
    app.run(debug=True)