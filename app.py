from flask import Flask, request, jsonify, render_template
from user_agents import parse
from datetime import datetime
import requests
import os  # <-- ต้อง import os เพื่ออ่าน environment variable

app = Flask(__name__)

# ใส่ Discord Webhook ผ่าน Environment Variable (ปลอดภัยกว่า)
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return render_template("index.html")  # หน้า HTML ของคุณ

@app.route("/log", methods=["POST"])
def log_visitor():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0]
    ua_string = request.headers.get("User-Agent", "")
    ua = parse(ua_string)
    data = request.json or {}

    message = f"""
🌐 **New Visitor**
Time: `{datetime.now().isoformat()}`
IP: `{ip}`
Device: `{ua.device.family}`
Device Type: `{"Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC"}`
OS: `{ua.os.family} {ua.os.version_string}`
Browser: `{ua.browser.family} {ua.browser.version_string}`
Language: `{request.headers.get("Accept-Language")}`
Screen: `{data.get("screen")}`
Platform: `{data.get("platform")}`
Timezone: `{data.get("timezone")}`
Touch Support: `{data.get("touch")}`
"""

    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Error sending to Discord:", e)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ใช้ port ของ Render
    app.run(host="0.0.0.0", port=port)        # host ต้องเป็น 0.0.0.0
