from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import urllib.parse

# Add parent directory to path so bot module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import PlatformModeratorBot, load_token

token = load_token()
bot = PlatformModeratorBot(token)
bot.bot_username = "platforminvest101bot"
bot.bot_id = 8840394969

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)

        host = self.headers.get("Host", "")
        proto = self.headers.get("X-Forwarded-Proto", "https")

        if "set_webhook" in params and host:
            webhook_url = f"{proto}://{host}/api"
            res = bot.request("setWebhook", {
                "url": webhook_url,
                "allowed_updates": ["message", "edited_message"]
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        payload = {
            "status": "online",
            "bot": "@platforminvest101bot",
            "mode": "Vercel Serverless Webhook",
            "setup": f"Visit {proto}://{host}/api?set_webhook=1 to bind Telegram webhook"
        }
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            update = json.loads(body.decode("utf-8"))

            if "message" in update:
                bot.handle_message(update["message"], is_edit=False)
            elif "edited_message" in update:
                bot.handle_message(update["edited_message"], is_edit=True)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
