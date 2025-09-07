# =========================
# Pro Telegram Userbot v3.1 (DM Only + Render Ready)
# =========================

from telethon import TelegramClient, events, errors
import random
import asyncio
import os
from flask import Flask

# -------------------------
# 🔹 CONFIG
# -------------------------
api_id = int(os.getenv("API_ID", "20223096"))  # from Render env
api_hash = os.getenv("API_HASH", "2de308bee63de3d6368380ce66b853ce")
session_name = os.getenv("SESSION_NAME", "userbot_session")

# Auto-reply messages
auto_replies = [
    "Hey! I'm currently offline, will reply later 😊",
    "Thanks for your message! I'll get back to you soon ⏳",
    "I'm away right now, talk soon 👍",
    "Busy right now, but I’ll reply ASAP 💬",
]

# -------------------------
# 🔹 VARIABLES
# -------------------------
offline_mode = True
missed_messages = {}

# -------------------------
# 🔹 TELETHON CLIENT
# -------------------------
client = TelegramClient(session_name, api_id, api_hash)

# -------------------------
# 🔹 DM HANDLER
# -------------------------


@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    global offline_mode, missed_messages

    try:
        sender = await event.get_sender()
        if sender is None or sender.is_self:
            return

        # 🚫 Skip groups/channels
        if event.is_group or event.is_channel:
            return

        username = sender.username or sender.first_name or "there"

        if offline_mode:
            missed_messages.setdefault(username, []).append(
                event.text or "<Non-text>"
            )

            # Reply once per user
            if len(missed_messages[username]) == 1:
                reply = random.choice(auto_replies)
                await event.reply(reply)

    except Exception as e:
        print(f"[Error in handle_message] {e}")

# -------------------------
# 🔹 COMMANDS
# -------------------------


@client.on(events.NewMessage(pattern=r'/offline'))
async def go_offline(event):
    global offline_mode
    offline_mode = True
    await event.reply("📴 You are now OFFLINE. Auto-replies active.")


@client.on(events.NewMessage(pattern=r'/online'))
async def go_online(event):
    global offline_mode, missed_messages
    offline_mode = False
    await event.reply("✅ You are now ONLINE.")

    if missed_messages:
        report = "📌 Missed messages:\n"
        for user, msgs in missed_messages.items():
            report += f"\n{user}:\n" + "\n".join(f" - {m}" for m in msgs)
        await event.reply(report)
        missed_messages = {}


@client.on(events.NewMessage(pattern=r'/missed'))
async def show_missed(event):
    global missed_messages
    if missed_messages:
        report = "📌 Missed messages:\n"
        for user, msgs in missed_messages.items():
            report += f"\n{user}:\n" + "\n".join(f" - {m}" for m in msgs)
        await event.reply(report)
    else:
        await event.reply("✅ No missed messages.")

# -------------------------
# 🔹 KEEPALIVE SERVER
# -------------------------
app = Flask(__name__)


@app.route('/')
def home():
    return "🤖 Userbot is alive on Render!"


# -------------------------
# 🔹 MAIN LOOP
# -------------------------
async def main():
    while True:
        try:
            print("🤖 Pro Userbot (Render Ready) is running...")
            await client.start()
            await client.run_until_disconnected()
        except (errors.FloodWaitError, errors.RPCError) as e:
            print(f"[Telegram Error] {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[Unexpected Error] {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    asyncio.run(main())
