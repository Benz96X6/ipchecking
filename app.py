from flask import Flask, request
from user_agents import parse
from datetime import datetime
import requests

app = Flask(__name__)

# 🔴 ใส่ Discord Webhook ของคุณ
WEBHOOK_URL = "https://discord.com/api/webhooks/1453051676423618590/-mvVCRBnzPKALk_3WqPx8AKL8vssSXBvOUIicvCfJieCl7EHmgQ_4qqIiJbKcxu1HyaW"

@app.route("/")
def home():
    # ดักจับ IP และ User-Agent ทุกคนที่เข้าหน้านี้
    ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0]
    ua_string = request.headers.get("User-Agent", "")
    ua = parse(ua_string)

    message = f"""
🌐 **New Visitor**
Time: `{datetime.now().isoformat()}`
IP: `{ip}`
Device: `{ua.device.family}`
Device Type: `{"Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC"}`
OS: `{ua.os.family} {ua.os.version_string}`
Browser: `{ua.browser.family} {ua.browser.version_string}`
Language: `{request.headers.get("Accept-Language")}`
"""

    # ส่งข้อมูลไป Discord
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Error sending to Discord:", e)

    return "Logged to Discord!"

if __name__ == "__main__":
    app.run(debug=True)
