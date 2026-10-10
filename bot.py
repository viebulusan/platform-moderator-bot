#!/usr/bin/env python3
"""
Telegram Group Moderator Bot (@platforminvest101bot)
---------------------------------------------------
Features:
1. Deletes "User joined the group" and "User left the group" service messages.
2. Deletes links/URLs/invite links sent by regular members (both new and edited messages).
3. Allows group administrators and group creator to send links freely.
4. Auto-greets group when invited and cleans up service notices.
5. Zero external dependencies - pure Python 3 standard library.
"""

import sys
import os
import json
import time
import re
import signal
import urllib.request
import urllib.parse
import urllib.error
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Comprehensive regex to detect URLs, domain names, shorteners, and invite links
LINK_REGEX = re.compile(
    r'(https?://[^\s]+)|'
    r'(ftp://[^\s]+)|'
    r'(tg://[^\s]+)|'
    r'(t\.me/[^\s]+)|'
    r'(telegram\.me/[^\s]+)|'
    r'(telegram\.dog/[^\s]+)|'
    r'(wa\.me/[^\s]+)|'
    r'(chat\.whatsapp\.com/[^\s]+)|'
    r'(discord\.gg/[^\s]+)|'
    r'(discord\.com/invite/[^\s]+)|'
    r'(www\.[^\s]+)|'
    r'(\b[a-zA-Z0-9-]+\.(?:com|org|net|io|me|xyz|ph|co|vip|app|site|top|cc|online|pro|info|live|shop|club|store|tech|fun|space|link|ai|gg|dev|biz|tv|edu|gov|us|uk|ru|ca|de|in|ly|to|ee|is|it|fr|nl|se|ch|es|win|icu|fit|loan|group|ltd|mobi|bid|work|zone|agency|network|media|digital|life|today|world|trade|click|cloud|run|page|lat|asia|bet|pub|center|money|finance|cash|fund)\b[^\s]*)',
    re.IGNORECASE
)

# Telegram system IDs for anonymous admins and service accounts
ANONYMOUS_ADMIN_ID = 1087968824
TELEGRAM_SERVICE_ID = 777000

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

class PlatformModeratorBot:
    def __init__(self, token: str):
        self.token = token.strip()
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.admin_cache = {}  # (chat_id, user_id) -> (is_admin, expire_time)
        self.admin_cache_lock = threading.Lock()
        self.bot_username = ""
        self.bot_id = None
        self.running = True

    def request(self, method: str, data: dict = None) -> dict:
        url = f"{self.api_url}/{method}"
        headers = {"Content-Type": "application/json"}
        req_data = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(url, data=req_data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=35) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                err_resp = json.loads(e.read().decode("utf-8"))
                return err_resp
            except Exception:
                return {"ok": False, "description": str(e)}
        except Exception as e:
            return {"ok": False, "description": str(e)}

    def delete_message(self, chat_id: int, message_id: int) -> bool:
        res = self.request("deleteMessage", {
            "chat_id": chat_id,
            "message_id": message_id
        })
        if not res.get("ok"):
            err_desc = res.get("description", "Unknown error")
            log(f"⚠️ deleteMessage failed for chat {chat_id}, msg {message_id}: {err_desc}")
            return False
        return True

    def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown", disable_web_page_preview: bool = True) -> dict:
        return self.request("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        })

    def is_user_admin(self, chat_id: int, user_id: int) -> bool:
        if not user_id:
            return False

        # Telegram service accounts or anonymous admins
        if user_id in [ANONYMOUS_ADMIN_ID, TELEGRAM_SERVICE_ID]:
            return True

        cache_key = (chat_id, user_id)
        now = time.time()

        with self.admin_cache_lock:
            if cache_key in self.admin_cache:
                is_adm, exp = self.admin_cache[cache_key]
                if now < exp:
                    return is_adm

        res = self.request("getChatMember", {
            "chat_id": chat_id,
            "user_id": user_id
        })
        if res.get("ok"):
            status = res.get("result", {}).get("status", "")
            is_admin = status in ["creator", "administrator"]
            with self.admin_cache_lock:
                self.admin_cache[cache_key] = (is_admin, now + 60)
            return is_admin

        return False

    def message_contains_links(self, msg: dict) -> bool:
        # 1. Check native Telegram message entities in text
        for ent in (msg.get("entities") or []):
            if ent.get("type") in ["url", "text_link"]:
                return True

        # 2. Check native entities in caption (photos, videos, docs, animations)
        for ent in (msg.get("caption_entities") or []):
            if ent.get("type") in ["url", "text_link"]:
                return True

        # 3. Check inline buttons (URL buttons or Web Apps)
        reply_markup = msg.get("reply_markup") or {}
        for row in (reply_markup.get("inline_keyboard") or []):
            for btn in row:
                if btn.get("url") or btn.get("web_app"):
                    return True

        # 4. Check regex patterns across text and caption
        text = msg.get("text") or ""
        caption = msg.get("caption") or ""
        combined = f"{text} {caption}".strip()
        if combined and LINK_REGEX.search(combined):
            return True

        return False

    def handle_message(self, msg: dict, is_edit: bool = False):
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type", "")
        chat_title = chat.get("title") or f"Chat {chat_id}"
        message_id = msg.get("message_id")

        if not chat_id or not message_id:
            return

        # -------------------------------------------------------------
        # Handle Private Chat Commands (/start, /help, /status)
        # -------------------------------------------------------------
        if chat_type == "private":
            text = (msg.get("text") or "").strip().lower()
            if text in ["/start", "/help", "/status", "/ping"]:
                self.send_message(
                    chat_id,
                    f"👋 Hello! I am *@{self.bot_username}* — Telegram Group Moderator Bot.\n\n"
                    "🛡️ *Features:*\n"
                    "• Automatically deletes **User joined the group** notices.\n"
                    "• Automatically deletes **User left the group** notices.\n"
                    "• Automatically deletes **Links & URLs** sent by regular members.\n"
                    "• Allows **Group Administrators** to send links freely.\n\n"
                    "📌 *Quick Setup Guide:*\n"
                    "1. Add @{self.bot_username} to your group chat.\n"
                    "2. Promote the bot to **Administrator**.\n"
                    "3. Grant the **Delete Messages** permission.\n\n"
                    "✅ The bot is 100% active and ready to protect your group!"
                )
            return

        # Only process group and supergroup messages
        if chat_type not in ["group", "supergroup"]:
            return

        # -------------------------------------------------------------
        # 1. Clean Service Messages ("User joined" / "User left")
        # -------------------------------------------------------------
        new_members = msg.get("new_chat_members") or []
        if "new_chat_participant" in msg and not new_members:
            new_members = [msg["new_chat_participant"]]
        if "new_chat_member" in msg and not new_members:
            new_members = [msg["new_chat_member"]]

        is_join = bool(new_members) or ("new_chat_members" in msg) or ("new_chat_participant" in msg) or ("new_chat_member" in msg)
        if is_join:
            # Delete join service message immediately
            deleted = self.delete_message(chat_id, message_id)
            names = ", ".join([u.get("first_name", "User") for u in new_members]) or "User"
            log(f"[CLEANUP] Deleted 'user joined' message (ID: {message_id}) for [{names}] in '{chat_title}' ({chat_id})")

            # Check if this bot was just invited to the group
            for member in new_members:
                if member.get("id") == self.bot_id:
                    log(f"[INVITED] Bot added to group '{chat_title}' ({chat_id})!")
                    welcome_resp = self.send_message(
                        chat_id,
                        f"🛡️ *@{self.bot_username} is now active in {chat_title}!*\n\n"
                        "I am configured to:\n"
                        "• Remove join and leave notices automatically.\n"
                        "• Remove links posted by regular members.\n"
                        "• Allow admins to share links freely.\n\n"
                        "⚠️ *Admin Notice:* Please ensure I am promoted to **Administrator** with **Delete Messages** permission so I can moderate this chat."
                    )
                    # Automatically delete welcome message after 30 seconds to keep chat clean
                    bot_msg_id = welcome_resp.get("result", {}).get("message_id") if welcome_resp.get("ok") else None
                    if bot_msg_id:
                        def cleanup_welcome():
                            self.delete_message(chat_id, bot_msg_id)
                        threading.Timer(30.0, cleanup_welcome).start()
            return

        is_leave = ("left_chat_member" in msg) or ("left_chat_participant" in msg)
        if is_leave:
            deleted = self.delete_message(chat_id, message_id)
            left_user = msg.get("left_chat_member") or msg.get("left_chat_participant") or {}
            left_name = left_user.get("first_name", "User")
            log(f"[CLEANUP] Deleted 'user left' message (ID: {message_id}) for [{left_name}] in '{chat_title}' ({chat_id})")
            return

        # -------------------------------------------------------------
        # 2. Check Sender Authority (Admin vs Regular Member)
        # -------------------------------------------------------------
        sender_chat = msg.get("sender_chat")
        from_user = msg.get("from", {})
        user_id = from_user.get("id")
        username = from_user.get("username") or from_user.get("first_name") or f"User-{user_id}"

        # Precise admin verification:
        is_admin = False
        if sender_chat and (sender_chat.get("id") == chat_id):
            # Sent as anonymous group admin
            is_admin = True
        elif user_id in [ANONYMOUS_ADMIN_ID, TELEGRAM_SERVICE_ID]:
            # Telegram system or anonymous bot
            is_admin = True
        elif user_id and self.is_user_admin(chat_id, user_id):
            # User is group admin or creator
            is_admin = True
        elif sender_chat:
            # Sent as a channel - check if the channel is recognized as admin
            is_admin = self.is_user_admin(chat_id, sender_chat.get("id"))

        # Admin helper command: /start, /status, /ping, /guard
        text = (msg.get("text") or "").strip().lower()
        bot_suffix = f"@{self.bot_username.lower()}" if self.bot_username else ""
        if is_admin and (text in ["/start", "/status", "/ping", "/guard", f"/start{bot_suffix}", f"/status{bot_suffix}", f"/ping{bot_suffix}", f"/guard{bot_suffix}"]):
            sent = self.send_message(
                chat_id,
                f"🛡️ *@{self.bot_username} Status in {chat_title}:*\n\n"
                "• *Join/Leave Notices:* Auto-removed ✅\n"
                "• *Member Links:* Blocked & Removed ✅\n"
                "• *Admin Links:* Allowed freely ✅\n"
                "• *Status:* 24/7 Active Protection"
            )
            bot_msg_id = sent.get("result", {}).get("message_id") if sent.get("ok") else None
            # Automatically delete command and reply after 8 seconds to prevent chat clutter
            def cleanup_cmd():
                if bot_msg_id:
                    self.delete_message(chat_id, bot_msg_id)
                self.delete_message(chat_id, message_id)
            threading.Timer(8.0, cleanup_cmd).start()
            return

        # Group Admins are exempt - allowed to post links freely!
        if is_admin:
            return

        # -------------------------------------------------------------
        # 3. Detect & Remove Links from Regular Members
        # -------------------------------------------------------------
        if self.message_contains_links(msg):
            deleted = self.delete_message(chat_id, message_id)
            action_desc = "edited message" if is_edit else "message"
            if deleted:
                log(f"[BLOCKED] Deleted link from member @{username} (ID: {user_id}) in {action_desc} (Chat: '{chat_title}', Msg ID: {message_id})")
            else:
                log(f"[WARNING] Failed to delete link from @{username} in '{chat_title}'. Ensure @{self.bot_username} is an Administrator with 'Delete Messages' permission!")

    def start_polling(self):
        log("==================================================")
        log(" 🛡️ Starting Telegram Group Moderator Bot...")
        log(" - Join/Leave Notice Removal: ACTIVE")
        log(" - Member Link Deletion: ACTIVE")
        log(" - Admin Link Exemption: ACTIVE")
        log("==================================================")

        me = self.request("getMe")
        if not me.get("ok"):
            log(f"❌ Failed to verify bot token: {me.get('description')}")
            sys.exit(1)

        result = me.get("result", {})
        self.bot_username = result.get("username", "")
        self.bot_id = result.get("id")
        bot_name = result.get("first_name", "Bot")
        log(f"✅ Successfully logged in as @{self.bot_username} ('{bot_name}', ID: {self.bot_id})")
        log("Listening for group updates...")

        while self.running:
            try:
                updates = self.request("getUpdates", {
                    "offset": self.last_update_id + 1,
                    "timeout": 25,
                    "allowed_updates": ["message", "edited_message"]
                })

                if updates.get("ok"):
                    for update in updates.get("result", []):
                        self.last_update_id = update.get("update_id")
                        if "message" in update:
                            self.handle_message(update["message"], is_edit=False)
                        elif "edited_message" in update:
                            self.handle_message(update["edited_message"], is_edit=True)
                else:
                    err_desc = updates.get("description", "Unknown error")
                    log(f"⚠️ getUpdates response: {err_desc}")
                    time.sleep(2)
            except KeyboardInterrupt:
                log("Bot stopped by user.")
                break
            except Exception as e:
                log(f"Polling error: {e}")
                time.sleep(3)

    def stop(self):
        self.running = False

def load_token() -> str:
    # 1. Command-line argument
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()

    # 2. Environment variable
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        return os.environ.get("TELEGRAM_BOT_TOKEN").strip()

    # 3. .env file
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.isfile(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # 4. Fallback provided token
    return "8840394969:AAFXsybR9ihgyRqBKe00r8eeILxl-G1mwc4"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        payload = {
            "status": "online",
            "service": "Telegram Group Moderator Bot",
            "bot": "@platforminvest101bot",
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def log_message(self, format, *args):
        # Silence routine health check requests from console output
        pass

def run_http_server(port: int):
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        log(f"🌐 HTTP health server listening on port {port} (Cloud & Local Ready)")
        server.serve_forever()
    except Exception as e:
        log(f"HTTP health server notice: {e}")

def keepalive_self_ping():
    """Keeps the bot awake on free-tier cloud hosting (e.g. Render) by pinging itself."""
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        return
    url = f"{render_url.rstrip('/')}/health"
    log(f"🔄 [KEEPALIVE] Auto self-ping active for {url}")
    while True:
        time.sleep(300)  # Ping every 5 minutes
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Render-Keepalive/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                pass
        except Exception as e:
            # Silent catch to prevent crash
            pass

def main():
    token = load_token()

    # Start HTTP health server for cloud hosting (Render / Railway / etc.)
    port = int(os.environ.get("PORT", "10000"))
    threading.Thread(target=run_http_server, args=(port,), daemon=True).start()

    # Start keepalive self-ping if running on Render
    threading.Thread(target=keepalive_self_ping, daemon=True).start()

    bot = PlatformModeratorBot(token)

    def sig_handler(sig, frame):
        log("Shutting down bot gracefully...")
        bot.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    bot.start_polling()

if __name__ == "__main__":
    main()

