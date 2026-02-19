import os
import logging
import asyncio

from telegram import Update
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError, RetryAfter
from telegram.ext import (
    Application,
    ContextTypes,
    ChatJoinRequestHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from db import add_user, get_all_users, remove_user, init_db

# ================= CONFIG =================
BOT_TOKEN = "7539536706:AAHk4mgyqv7AHw9tWHqA7K_5d1qNOgFXPQ8"
ADMIN_ID = [7849592882]  # ✅ multi admin supported
APK_PATH = "𝗥ᴀᴊᴀ_𝗚ᴀᴍᴇ_𝗣ᴀɴᴇʟ_𝗛ᴀᴄᴋ.apk"
VOICE_PATH = "VOICEHACK.ogg"
# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ================= WELCOME PACKAGE =================
async def send_welcome_package(user, context: ContextTypes.DEFAULT_TYPE):
    add_user(user.id)

    welcome_message = f"""
👋🏻 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 {user.mention_html()} 𝐁𝐑𝐎𝐓𝐇𝐄𝐑 𝐓𝐎 𝗢𝗨𝗥 - 𝐑𝐀𝐉𝐀 𝐏𝐑𝐈𝐕𝐀𝐓𝐄 𝐇𝐀𝐂𝐊 𝐒𝐄𝐑𝐕𝐄𝐑 🤑💵
"""

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_message,
            parse_mode="HTML",
        )
    except Exception:
        return

    # APK
    if os.path.exists(APK_PATH):
        try:
            with open(APK_PATH, "rb") as apk:
                await context.bot.send_document(
                    chat_id=user.id,
                    document=apk,
                    caption="""📂 ☆𝟏𝟎𝟎% 𝐍𝐔𝐌𝐁𝐄𝐑 𝐇𝐀𝐂𝐊💸

(केवल प्रीमियम उपयोगकर्ताओं के लिए)💎
(𝟏𝟎𝟎% नुकसान की भरपाई की गारंटी)🧬

♻सहायता के लिए @RDX_SONU_01
🔴हैक का उपयोग कैसे करें
https://t.me/rajaindiaprediction/54""",
                )
        except Exception as e:
            logging.error(f"APK send error: {e}")

    # VOICE
    if os.path.exists(VOICE_PATH):
        try:
            with open(VOICE_PATH, "rb") as voice:
                await context.bot.send_voice(
                    chat_id=user.id,
                    voice=voice,
                    caption="""🎙 सदस्य 9X गुना लाभ का प्रमाण 👇🏻
https://t.me/rajaindiaprediction/56

♻सहायता के लिए @RDX_SONU_01
लगातार नंबर पे नंबर जीतना 🤑♻👑""",
                )
        except Exception as e:
            logging.error(f"Voice send error: {e}")


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    logging.info(f"User added: {user.id}")

    await send_welcome_package(user, context)


# ================= AUTO CAPTURE =================
async def capture_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        add_user(user.id)


# ================= JOIN REQUEST =================
async def approve_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    if not request:
        return

    user = request.from_user
    await send_welcome_package(user, context)


# ================= SAFE COPY =================
async def send_copy_safe(context, message, user_id):
    try:
        await message.copy(chat_id=user_id)
        return "ok"

    except Forbidden:
        return "blocked"

    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        try:
            await message.copy(chat_id=user_id)
            return "ok"
        except Exception:
            return "failed"

    except (BadRequest, TimedOut, NetworkError):
        return "failed"

    except Exception as e:
        logging.error(f"Copy error for {user_id}: {e}")
        return "failed"


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Reply to a message to broadcast.")
        return

    all_users = get_all_users()
    users = [u for u in all_users if u not in ADMIN_ID]

    total_users = len(users)

    if total_users == 0:
        await update.message.reply_text("⚠️ No users in database.")
        return

    progress_msg = await update.message.reply_text(
        f"🚀 Broadcast started...\n\n👥 Total Users: {total_users}"
    )

    delivered = 0
    failed = 0
    removed = 0

    BATCH_SIZE = 25
    DELAY = 1.2

    for i in range(0, total_users, BATCH_SIZE):
        batch = users[i:i + BATCH_SIZE]

        tasks = [
            send_copy_safe(context, update.message.reply_to_message, uid)
            for uid in batch
        ]

        results = await asyncio.gather(*tasks)

        for result, uid in zip(results, batch):
            if result == "ok":
                delivered += 1
            elif result == "blocked":
                remove_user(uid)
                removed += 1
                failed += 1
            else:
                failed += 1

        try:
            await progress_msg.edit_text(
                f"🚀 Broadcasting...\n\n"
                f"👥 Total: {total_users}\n"
                f"✅ Delivered: {delivered}\n"
                f"❌ Failed: {failed}\n"
                f"🗑 Removed: {removed}"
            )
        except Exception:
            pass

        await asyncio.sleep(DELAY)

    await progress_msg.edit_text(
        f"✅ Broadcast Completed!\n\n"
        f"👥 Total: {total_users}\n"
        f"✅ Delivered: {delivered}\n"
        f"❌ Failed: {failed}\n"
        f"🗑 Removed: {removed}"
    )


# ================= USERS COUNT =================
async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return

    total = len(get_all_users())
    await update.message.reply_text(f"👥 Total Users: {total}")


# ================= MAIN =================
def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("users", users_count))
    app.add_handler(ChatJoinRequestHandler(approve_and_send))

    # ⭐ AUTO CAPTURE — MUST BE LAST
    app.add_handler(MessageHandler(filters.ALL, capture_user))

    app.run_polling(allowed_updates=["message", "chat_join_request"])


if __name__ == "__main__":
    main()
