# ==========================
# DILHUX AI PRO V2
# Arabic AI Assistant
# ==========================

import requests
import json
import os
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# ==========================
# SETTINGS
# ==========================

TELEGRAM_TOKEN = "8606696347:AAFM_hLL4iQRBOpobGSs9DB4_MEZYHNUTUM"

GROQ_KEY = "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"

ADMIN_ID =7768895580


# ==========================
# FILES
# ==========================

USERS_FILE = "users.json"
MEMORY_FILE = "memory.json"
BANNED_FILE = "banned.json"



def load_file(name):

    if os.path.exists(name):

        try:
            with open(
                name,
                "r",
                encoding="utf-8"
            ) as f:
                return json.load(f)

        except:
            return {}

    return {}



def save_file(name, data):

    with open(
        name,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )



users = load_file(USERS_FILE)

memory = load_file(MEMORY_FILE)

banned = load_file(BANNED_FILE)

broadcast_mode = {}



# ==========================
# MENU
# ==========================

def menu(uid):

    buttons = [

        ["🤖 AI Chat"],

        ["👑 Admin Panel"]

    ]


    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )



# ==========================
# START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    uid = str(user.id)


    users[uid] = {

        "name": user.first_name,

        "date": str(datetime.now())

    }


    save_file(
        USERS_FILE,
        users
    )


    await update.message.reply_text(

        "مرحبا بك 👋\n\n"
        "أنا DILHUX AI PRO 🤖\n"
        "مساعد ذكاء اصطناعي.\n"
        "أجب باللغة العربية فقط.",

        reply_markup=menu(user.id)

    )# ==========================
# ADMIN PANEL
# ==========================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.message.from_user.id

    if uid != ADMIN_ID:

        await update.message.reply_text(
            "❌ ليس لديك صلاحية."
        )

        return


    await update.message.reply_text(

        "👑 Admin Panel\n\n"
        "/stats - إحصائيات\n"
        "/users - المستخدمون\n"
        "/broadcast - إرسال للجميع"

    )



# ==========================
# STATS
# ==========================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.message.from_user.id


    if uid != ADMIN_ID:

        return


    await update.message.reply_text(

        "📊 DILHUX AI PRO\n\n"
        f"👥 Users: {len(users)}\n"
        f"🧠 Memory: {len(memory)}\n"
        f"🚫 Banned: {len(banned)}"

    )



# ==========================
# USERS
# ==========================

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.message.from_user.id


    if uid != ADMIN_ID:

        return


    text = "👥 Users:\n\n"


    for user_id, data in users.items():

        text += (
            f"🆔 {user_id}\n"
            f"👤 {data.get('name','Unknown')}\n\n"
        )


    await update.message.reply_text(text)



# ==========================
# BROADCAST START
# ==========================

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = str(update.message.from_user.id)


    if int(uid) != ADMIN_ID:

        return


    broadcast_mode[uid] = True


    await update.message.reply_text(

        "📢 اكتب الرسالة التي تريد إرسالها للجميع."

    )



# ==========================
# AI CHAT
# ==========================

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = str(update.message.from_user.id)

    text = update.message.text



    # BROADCAST

    if broadcast_mode.get(uid):

        broadcast_mode[uid] = False


        for user_id in users:

            try:

                await context.bot.send_message(

                    chat_id=user_id,

                    text=text

                )

            except:

                pass


        await update.message.reply_text(

            "✅ تم إرسال الرسالة للجميع."

        )

        return



    if uid in banned:

        await update.message.reply_text(

            "❌ أنت محظور."

        )

        return



    if uid not in memory:

        memory[uid] = []


    memory[uid].append({

        "role": "user",

        "content": text

    })


    history = memory[uid][-10:]


    url = "https://api.groq.com/openai/v1/chat/completions"


    headers = {

        "Authorization": f"Bearer {GROQ_KEY}",

        "Content-Type": "application/json"

    }


    data = {

        "model": "llama-3.3-70b-versatile",

        "messages": [

            {

                "role": "system",

                "content":

                "أنت DILHUX AI PRO. "
                "أجب باللغة العربية فقط. "
                "كن مساعداً ذكياً ومهذباً."

            }

        ] + history

    }


    try:

        r = requests.post(

            url,

            headers=headers,

            json=data,

            timeout=60

        )


        result = r.json()


        answer = result["choices"][0]["message"]["content"]


    except Exception as e:

        answer = "خطأ:\n" + str(e)



    memory[uid].append({

        "role": "assistant",

        "content": answer

    })


    save_file(

        MEMORY_FILE,

        memory

    )


    await update.message.reply_text(answer)# ==========================
# BOT START
# ==========================


app = Application.builder().token(
    TELEGRAM_TOKEN
).build()



# COMMANDS

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    CommandHandler(
        "stats",
        stats
    )
)


app.add_handler(
    CommandHandler(
        "users",
        users_list
    )
)


app.add_handler(
    CommandHandler(
        "broadcast",
        broadcast_start
    )
)



# ADMIN BUTTON

app.add_handler(
    MessageHandler(
        filters.Regex("👑 Admin Panel"),
        admin_panel
    )
)



# AI CHAT

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ai_chat
    )
)



print(
    "DILHUX AI PRO V2 Running..."
)



app.run_polling()from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "DILHUX AI PRO V2 Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()