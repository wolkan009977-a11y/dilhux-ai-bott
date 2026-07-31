# =====================================
# DILHUX AI PRO V3
# Smart Telegram AI Assistant
# =====================================

import os
import json
import requests
from datetime import datetime
from threading import Thread

from flask import Flask


from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
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

BOT_TOKEN = os.getenv("BOT_TOKEN")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


# ==========================
# FILES
# ==========================

USERS_FILE = "users.json"
MEMORY_FILE = "memory.json"
BANNED_FILE = "banned.json"


def load_data(file):

    if os.path.exists(file):

        try:
            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:
                return json.load(f)

        except:
            return {}

    return {}


def save_data(file, data):

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


users = load_data(USERS_FILE)

memory = load_data(MEMORY_FILE)

banned = load_data(BANNED_FILE)

broadcast_mode = {}

#==========================
# MENU
# ==========================

def menu():

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

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    uid = str(user.id)


    users[uid] = {

        "name": user.first_name,

        "username": user.username,

        "join_date": str(datetime.now())

    }


    save_data(
        USERS_FILE,
        users
    )


    keyboard = [
        [
            InlineKeyboardButton(
                "🍽 دىلخۇش ئارامگاھى تىزىملىكى",
                url="https://dilhux-aramgah-web.onrender.com/"
            )
        ]
    ]


    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.message.reply_text(

        "🌹 دىلخۇش ئارامگاھىغا خۇش كەلدىڭىز\n\n"
        "تىزىملىكنى كۆرۈش ئۈچۈن تۆۋەندىكى كۇنۇپكىنى بېسىڭ:",

        reply_markup=reply_markup

    )


# ==========================
# ADMIN PANEL
# ==========================

async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id


    if uid != ADMIN_ID:

        await update.message.reply_text(
            "❌ ليس لديك صلاحية."
        )

        return


    await update.message.reply_text(

        "👑 DILHUX ADMIN PANEL\n\n"

        "📊 /stats - الإحصائيات\n"

        "👥 /users - قائمة المستخدمين\n"

        "📢 /broadcast - إرسال للجميع\n"

        "🚫 /ban ID - حظر مستخدم\n"

        "✅ /unban ID - فك الحظر"

    )# ==========================
# STATS
# ==========================

async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return


    await update.message.reply_text(

        "📊 DILHUX AI PRO V3\n\n"

        f"👥 Users: {len(users)}\n"

        f"🧠 Memory Users: {len(memory)}\n"

        f"🚫 Banned: {len(banned)}"

    )


# ==========================
# USERS LIST
# ==========================

async def users_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return


    text = "👥 Users:\n\n"


    for user_id, data in users.items():

        text += (

            f"🆔 {user_id}\n"

            f"👤 {data.get('name','Unknown')}\n"

            f"📅 {data.get('join_date','')}\n\n"

        )


    await update.message.reply_text(text[:4000])


# ==========================
# BROADCAST
# ==========================

async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return


    broadcast_mode[str(uid)] = True


    await update.message.reply_text(

        "📢 اكتب الرسالة الآن وسأرسلها للجميع."

    )


# ==========================
# BAN USER
# ==========================

async def ban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return


    if not context.args:

        await update.message.reply_text(
            "اكتب ID المستخدم."
        )

        return


    user_id = context.args[0]


    banned[user_id] = True


    save_data(
        BANNED_FILE,
        banned
    )


    await update.message.reply_text(

        f"🚫 تم حظر المستخدم {user_id}"

    )


# ==========================
# UNBAN USER
# ==========================

async def unban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return


    if not context.args:

        await update.message.reply_text(
            "اكتب ID المستخدم."
        )

        return


    user_id = context.args[0]


    if user_id in banned:

        del banned[user_id]


    save_data(
        BANNED_FILE,
        banned
    )


    await update.message.reply_text(

    f"✅ تم فك الحظر عن {user_id}"

    )
# AI CHAT
# ==========================

async def ai_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    uid = str(update.effective_user.id)

    text = update.message.text


    # Broadcast mode

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



    # Ban check

    if uid in banned:

        await update.message.reply_text(

            "❌ أنت محظور من استخدام البوت."

        )

        return



    # Memory create

    if uid not in memory:

        memory[uid] = []



    memory[uid].append({

        "role": "user",

        "content": text

    })


    history = memory[uid][-10:]


    # Groq API

    url = "https://api.groq.com/openai/v1/chat/completions"


    headers = {

        "Authorization":
        f"Bearer {GROQ_API_KEY}",

        "Content-Type":
        "application/json"

    }



    data = {

        "model":
        "llama-3.3-70b-versatile",


        "messages": [

            {

                "role": "system",

                "content":

                "أنت DILHUX AI PRO V3. "
                "أجب باللغة العربية فقط. "
                "كن ذكياً ومهذباً."

            }

        ] + history

    }



    try:

        response = requests.post(

            url,

            headers=headers,

            json=data,

            timeout=60

        )


        result = response.json()


        answer = result["choices"][0]["message"]["content"]



    except Exception as e:


        answer = (

            "حدث خطأ في الذكاء الاصطناعي:\n"

            + str(e)

        )



    memory[uid].append({

        "role": "assistant",

        "content": answer

    })


    save_data(

        MEMORY_FILE,

        memory

    )



    await update.message.reply_text(

        answer

    )# ==========================
# BOT START
# ==========================


application = Application.builder().token(
    BOT_TOKEN
).build()



# ==========================
# COMMANDS
# ==========================

application.add_handler(
    CommandHandler(
        "start",
        start
    )
)


application.add_handler(
    CommandHandler(
        "stats",
        stats
    )
)


application.add_handler(
    CommandHandler(
        "users",
        users_list
    )
)


application.add_handler(
    CommandHandler(
        "broadcast",
        broadcast
    )
)


application.add_handler(
    CommandHandler(
        "ban",
        ban
    )
)


application.add_handler(
    CommandHandler(
        "unban",
        unban
    )
)



# ==========================
# BUTTONS
# ==========================

application.add_handler(

    MessageHandler(

        filters.Regex("👑 Admin Panel"),

        admin_panel

    )

)



# ==========================
# TEXT AI CHAT
# ==========================

application.add_handler(

    MessageHandler(

        filters.TEXT & ~filters.COMMAND,

        ai_chat

    )

)



# ==========================
# FLASK SERVER
# ==========================


web_app = Flask(__name__)


@web_app.route("/")

def home():

    return "DILHUX AI PRO V3 Running!"



def run_web():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    web_app.run(

        host="0.0.0.0",

        port=port

    )



# Start Flask thread

Thread(
    target=run_web
).start()



print(
    "DILHUX AI PRO V3 Running..."
)



# Start Telegram Bot

application.run_polling()
